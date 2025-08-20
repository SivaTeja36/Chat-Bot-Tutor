"""adding is_active column in kids table

Revision ID: 5ec4f3a9f12e
Revises: daac12dff066
Create Date: 2025-08-20 13:34:59.129919

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ec4f3a9f12e'
down_revision = 'daac12dff066'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add as nullable with server_default
    op.add_column('kids', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()))
    # Step 2: Update all existing records to True
    op.execute('UPDATE kids SET is_active = TRUE')
    # Step 3: Alter column to non-nullable
    op.alter_column('kids', 'is_active', nullable=False)
    # (server_default may remain if desired for future inserts)

def downgrade() -> None:
    op.drop_column('kids', 'is_active')
