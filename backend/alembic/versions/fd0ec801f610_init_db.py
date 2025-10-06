"""init db

Revision ID: fd0ec801f610
Revises: 
Create Date: 2025-09-30 09:42:54.383060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd0ec801f610'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'report_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(), nullable=False),
        sa.Column('response', sa.String(), nullable=True),
        sa.Column('report_type', sa.String(), server_default='basic', nullable=True),
        sa.Column('credits_used', sa.Integer(), server_default='1', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_usage_id'), 'report_usage', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_report_usage_id'), table_name='report_usage')
    op.drop_table('report_usage')
