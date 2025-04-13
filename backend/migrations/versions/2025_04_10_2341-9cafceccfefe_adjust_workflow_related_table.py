"""adjust workflow related table

Revision ID: 9cafceccfefe
Revises: 26914198668b
Create Date: 2025-04-10 23:41:52.962888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9cafceccfefe'
down_revision: Union[str, None] = '26914198668b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. create new enum type
    op.execute("CREATE TYPE operatorname AS ENUM ('LLM', 'END', 'START')")
    
    # 2. update column type
    op.alter_column('workflow_nodes', 'node_type',
               existing_type=postgresql.ENUM('LLM', 'END', 'START', name='workflownodetype'),
               type_=sa.Enum('LLM', 'END', 'START', name='operatorname'),
               existing_comment='Type of operation this node performs',
               existing_nullable=False,
               postgresql_using="node_type::text::operatorname")  # 添加类型转换
    
    # 3. drop old enum type
    op.execute("DROP TYPE workflownodetype")


def downgrade() -> None:
    # 1. create old enum type
    op.execute("CREATE TYPE workflownodetype AS ENUM ('LLM', 'END', 'START')")
    
    # 2. update column type
    op.alter_column('workflow_nodes', 'node_type',
               existing_type=sa.Enum('LLM', 'END', 'START', name='operatorname'),
               type_=postgresql.ENUM('LLM', 'END', 'START', name='workflownodetype'),
               existing_comment='Type of operation this node performs',
               existing_nullable=False,
               postgresql_using="node_type::text::workflownodetype")  # 添加类型转换
    
    # 3. drop new enum type
    op.execute("DROP TYPE operatorname")
