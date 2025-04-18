"""adjust conversation/message table

Revision ID: 16e8bcf809a2
Revises: 24fa5710d0ee
Create Date: 2025-04-18 12:36:09.979354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '16e8bcf809a2'
down_revision: Union[str, None] = '24fa5710d0ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. delete message column  
    op.drop_column('messages', 'message')
    
    # 2. truncate table messages(UUID can't be converted to int)
    op.execute('TRUNCATE TABLE messages CASCADE')
    
    # 3. modify id column type, use USING clause to force conversion
    # note: because the table has been truncated, any legal integer value can be used here
    op.execute('ALTER TABLE messages ALTER COLUMN id TYPE INTEGER USING 1')
    
    # 4. set id as an auto-increment column
    op.execute('CREATE SEQUENCE messages_id_seq')
    op.execute('ALTER TABLE messages ALTER COLUMN id SET DEFAULT nextval(\'messages_id_seq\')')
    op.execute('ALTER SEQUENCE messages_id_seq OWNED BY messages.id')
    
    # 5. add other new columns
    op.add_column('messages', sa.Column('execution_id', sa.UUID(), nullable=True, comment='Execution id'))
    op.add_column('messages', sa.Column('content', sa.Text(), nullable=False, comment='Message content'))
    op.add_column('messages', sa.Column('search_results', sa.JSON(), nullable=True, comment='Search results'))
    op.add_column('messages', sa.Column('thinking_content', sa.Text(), nullable=True, comment='Thinking process'))
    op.add_column('messages', sa.Column('files', sa.JSON(), nullable=True, comment='Files'))
    op.add_column('conversations', sa.Column('message_count', sa.Integer(), nullable=False, comment='Number of messages in the conversation'))
    op.add_column('conversations', sa.Column('last_message_id', sa.UUID(), nullable=True, comment='Last message id'))
    op.alter_column('conversations', 'summary',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.String(length=500),
               existing_comment='Conversation summary',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # 1. delete the new added columns
    op.drop_column('messages', 'files')
    op.drop_column('messages', 'thinking_content')
    op.drop_column('messages', 'search_results')
    op.drop_column('messages', 'content')
    op.drop_column('messages', 'execution_id')
    
    # 2. delete the sequence
    op.execute('DROP SEQUENCE IF EXISTS messages_id_seq')
    
    # 3. revert id column type to UUID
    op.execute('ALTER TABLE messages ALTER COLUMN id TYPE UUID USING gen_random_uuid()')
    
    # 4. add back the original message column
    op.add_column('messages', sa.Column('message', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False, comment='Message content in JSON format'))
    op.alter_column('conversations', 'summary',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=1000),
               existing_comment='Conversation summary',
               existing_nullable=True)
    op.drop_column('conversations', 'last_message_id')
    op.drop_column('conversations', 'message_count')
    # ### end Alembic commands ###
