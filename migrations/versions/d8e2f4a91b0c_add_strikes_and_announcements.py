"""Add account_strikes and announcement_logs tables

Revision ID: d8e2f4a91b0c
Revises: 1164e037907f
Create Date: 2026-06-15 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = 'd8e2f4a91b0c'
down_revision = '1164e037907f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'account_strikes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('issued_by_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.VARCHAR(length=32), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('reason', mysql.TEXT(), nullable=False),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', mysql.TIMESTAMP(), nullable=True),
        sa.Column('active', mysql.BOOLEAN(), server_default='1', nullable=False),
        sa.Column('action_taken', sa.VARCHAR(length=16), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['issued_by_id'], ['accounts.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'announcement_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', mysql.TEXT(), nullable=False),
        sa.Column('message', mysql.TEXT(), nullable=False),
        sa.Column('sent_by_id', sa.Integer(), nullable=True),
        sa.Column('sent_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('success', mysql.BOOLEAN(), server_default='1', nullable=False),
        sa.Column('error_message', mysql.TEXT(), nullable=True),
        sa.ForeignKeyConstraint(['sent_by_id'], ['accounts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('announcement_logs')
    op.drop_table('account_strikes')
