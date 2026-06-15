"""Add dashboard_settings table

Revision ID: c4a8f1e2b3d0
Revises: 1164e037907f
Create Date: 2026-06-15 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c4a8f1e2b3d0'
down_revision = '1164e037907f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'dashboard_settings',
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('value', mysql.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint('key')
    )


def downgrade():
    op.drop_table('dashboard_settings')
