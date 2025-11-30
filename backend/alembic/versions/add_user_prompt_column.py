"""add_user_prompt_column

Revision ID: add_user_prompt_column
Revises: add_user_id_columns
Create Date: 2025-11-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_prompt_column'
down_revision = 'add_user_id_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_prompt column to sessions table
    op.add_column('sessions', sa.Column('user_prompt', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove user_prompt column from sessions table
    op.drop_column('sessions', 'user_prompt')
