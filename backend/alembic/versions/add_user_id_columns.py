"""Add missing user_id columns to tables

Revision ID: add_user_id_columns
Revises: 3fdaf592f4da
Create Date: 2025-11-30 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_id_columns'
down_revision: Union[str, None] = '3fdaf592f4da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id to sessions table
    op.add_column('sessions', sa.Column('user_id', sa.String(length=36), nullable=True))
    
    # Add user_id to projects table
    op.add_column('projects', sa.Column('user_id', sa.String(length=36), nullable=True))
    
    # Add user_id to chat_history table
    op.add_column('chat_history', sa.Column('user_id', sa.String(length=36), nullable=True))


def downgrade() -> None:
    # Remove user_id from chat_history table
    op.drop_column('chat_history', 'user_id')
    
    # Remove user_id from projects table
    op.drop_column('projects', 'user_id')
    
    # Remove user_id from sessions table
    op.drop_column('sessions', 'user_id')
