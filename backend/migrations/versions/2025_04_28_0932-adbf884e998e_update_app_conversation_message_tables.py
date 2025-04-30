"""update app/conversation/message tables

Revision ID: adbf884e998e
Revises: 776c79b7a905
Create Date: 2025-04-28 09:32:24.421667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'adbf884e998e'
down_revision: Union[str, None] = '776c79b7a905'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE appstatus AS ENUM ('ACTIVE', 'INACTIVE', 'DEPRECATED', 'ARCHIVED')")
    op.drop_index('idx_version_published', table_name='app_versions')
    op.drop_index('idx_version_status', table_name='app_versions')
    op.drop_index('ix_app_versions_created_at', table_name='app_versions')
    op.drop_index('ix_app_versions_updated_at', table_name='app_versions')
    op.drop_index('uk_app_version', table_name='app_versions')
    op.add_column('apps', sa.Column('workflow_id', sa.UUID(), nullable=True))
    op.add_column('apps', sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'DEPRECATED', 'ARCHIVED', name='appstatus'), 
                                   server_default='ACTIVE', 
                                   nullable=False, 
                                   comment='Status of the application version'))
    op.alter_column('apps', 'description',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.Text(),
               existing_comment='Description of the application',
               existing_nullable=True)
    op.drop_index('idx_app_version', table_name='apps')
    op.create_index('idx_app_workflow', 'apps', ['workflow_id'], unique=False)
    op.create_foreign_key(None, 'apps', 'workflows', ['workflow_id'], ['id'], ondelete='SET NULL')
    op.drop_column('apps', 'version')
    op.add_column('conversations', sa.Column('description', sa.Text(), nullable=True, comment='Conversation description'))
    op.add_column('conversations', sa.Column('app_id', sa.UUID(), nullable=False, comment='Reference to the app'))
    op.create_index('idx_conversation_app', 'conversations', ['app_id'], unique=False)
    op.create_foreign_key(None, 'conversations', 'apps', ['app_id'], ['id'], ondelete='CASCADE')
    op.add_column('messages', sa.Column('workflow_id', sa.UUID(), nullable=True, comment='Reference to the specific workflow'))
    op.add_column('messages', sa.Column('workflow_version', sa.String(length=50), nullable=True, comment='Workflow version'))
    op.add_column('messages', sa.Column('workflow_run_id', sa.UUID(), nullable=True, comment='Workflow version id'))
    op.add_column('messages', sa.Column('updated_by', sa.UUID(), nullable=True, comment='User who updated the message (only for user messages)'))
    op.add_column('messages', sa.Column('error', sa.Text(), nullable=True, comment='Error message'))
    op.add_column('messages', sa.Column('images', sa.JSON(), nullable=True, comment='Images'))
    op.add_column('messages', sa.Column('audios', sa.JSON(), nullable=True, comment='Audios'))
    op.add_column('messages', sa.Column('tools', sa.JSON(), nullable=True, comment='Tools'))
    op.add_column('messages', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('messages', 'content',
               existing_type=sa.TEXT(),
               nullable=True,
               existing_comment='Message content')
    op.alter_column('messages', 'id',
               existing_type=sa.INTEGER(),
               comment=None,
               existing_comment='Unique identifier for the message',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('messages', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               comment=None,
               existing_comment='Timestamp when the message was created',
               existing_nullable=False)
    op.drop_index('idx_message_app_version', table_name='messages')
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    op.create_index(op.f('ix_messages_updated_at'), 'messages', ['updated_at'], unique=False)
    op.drop_constraint('messages_app_version_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key(None, 'messages', 'workflows', ['workflow_id'], ['id'], ondelete='SET NULL')
    op.drop_column('messages', 'search_results')
    op.drop_column('messages', 'app_version_id')
    op.drop_column('messages', 'execution_id')
    op.drop_table('app_versions')


def downgrade() -> None:
    op.create_table('app_versions',
    sa.Column('app_id', sa.UUID(), autoincrement=False, nullable=False, comment='Reference to the parent application'),
    sa.Column('version', sa.VARCHAR(length=50), autoincrement=False, nullable=False, comment='Version number'),
    sa.Column('workflow_version', sa.VARCHAR(length=50), autoincrement=False, nullable=False, comment='Associated workflow version'),
    sa.Column('published_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False, comment='Publication timestamp'),
    sa.Column('published_by', sa.UUID(), autoincrement=False, nullable=False, comment='User who published this version'),
    sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'DEPRECATED', 'ARCHIVED', name='appversionstatus'), autoincrement=False, nullable=False, comment='Version status'),
    sa.Column('snapshot', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False, comment='Version snapshot data'),
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('workflow_id', sa.UUID(), autoincrement=False, nullable=False, comment='Reference to the parent workflow'),
    sa.ForeignKeyConstraint(['app_id'], ['apps.id'], name='app_versions_app_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='app_versions_pkey')
    )
    op.add_column('messages', sa.Column('execution_id', sa.UUID(), autoincrement=False, nullable=True, comment='Execution id'))
    op.add_column('messages', sa.Column('app_version_id', sa.UUID(), autoincrement=False, nullable=True, comment='Reference to the specific app version'))
    op.add_column('messages', sa.Column('search_results', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True, comment='Search results'))
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.create_foreign_key('messages_app_version_id_fkey', 'messages', 'app_versions', ['app_version_id'], ['id'], ondelete='SET NULL')
    op.drop_index(op.f('ix_messages_updated_at'), table_name='messages')
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.create_index('idx_message_app_version', 'messages', ['app_version_id'], unique=False)
    op.alter_column('messages', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               comment='Timestamp when the message was created',
               existing_nullable=False)
    op.alter_column('messages', 'id',
               existing_type=sa.INTEGER(),
               comment='Unique identifier for the message',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('messages', 'content',
               existing_type=sa.TEXT(),
               nullable=False,
               existing_comment='Message content')
    op.drop_column('messages', 'updated_at')
    op.drop_column('messages', 'tools')
    op.drop_column('messages', 'audios')
    op.drop_column('messages', 'images')
    op.drop_column('messages', 'error')
    op.drop_column('messages', 'updated_by')
    op.drop_column('messages', 'workflow_run_id')
    op.drop_column('messages', 'workflow_version')
    op.drop_column('messages', 'workflow_id')
    op.drop_constraint(None, 'conversations', type_='foreignkey')
    op.drop_index('idx_conversation_app', table_name='conversations')
    op.drop_column('conversations', 'app_id')
    op.drop_column('conversations', 'description')
    op.add_column('apps', sa.Column('version', sa.VARCHAR(length=50), autoincrement=False, nullable=True, comment='Current version number'))
    op.drop_constraint(None, 'apps', type_='foreignkey')
    op.drop_index('idx_app_workflow', table_name='apps')
    op.create_index('idx_app_version', 'apps', ['version'], unique=False)
    op.alter_column('apps', 'description',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=1000),
               existing_comment='Description of the application',
               existing_nullable=True)
    op.drop_column('apps', 'status')
    op.drop_column('apps', 'workflow_id')
    op.create_index('uk_app_version', 'app_versions', ['app_id', 'version'], unique=True)
    op.create_index('ix_app_versions_updated_at', 'app_versions', ['updated_at'], unique=False)
    op.create_index('ix_app_versions_created_at', 'app_versions', ['created_at'], unique=False)
    op.create_index('idx_version_status', 'app_versions', ['status'], unique=False)
    op.create_index('idx_version_published', 'app_versions', ['published_at'], unique=False)
    op.execute("DROP TYPE appstatus")
