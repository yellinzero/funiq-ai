"""adjust conversation issue

Revision ID: 9ea2e0c330e8
Revises: af9c6b064888
Create Date: 2025-04-20 16:41:47.032061

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ea2e0c330e8'
down_revision: Union[str, None] = 'af9c6b064888'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing UUID column
    op.drop_column('conversations', 'last_message_id')
    
    # Add new Integer column
    op.add_column('conversations',
        sa.Column('last_message_id', sa.Integer(), nullable=True, comment='Last message id')
    )


def downgrade() -> None:
    # Drop the Integer column
    op.drop_column('conversations', 'last_message_id')
    
    # Add back UUID column
    op.add_column('conversations',
        sa.Column('last_message_id', postgresql.UUID(), nullable=True, comment='Last message id')
    )
