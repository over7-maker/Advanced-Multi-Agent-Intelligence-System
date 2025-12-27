# alembic/versions/004_add_feedback_table.py
"""Add feedback table for landing page

Revision ID: 004
Revises: 003_fix_task_results_schema
Create Date: 2025-12-27 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004'
down_revision = '003_fix_task_results_schema'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create feedback table for landing page feedback submissions"""
    
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feedback_id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sentiment', sa.String(50), nullable=True),  # 'positive', 'neutral', 'negative'
        sa.Column('page_context', sa.String(255), nullable=True),  # Which page the feedback came from
        sa.Column('email_sent', sa.Boolean(), nullable=True, server_default='false'),  # Whether confirmation email was sent
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('feedback_id')
    )
    
    # Create indexes for common queries
    op.create_index(op.f('ix_feedback_feedback_id'), 'feedback', ['feedback_id'])
    op.create_index(op.f('ix_feedback_email'), 'feedback', ['email'])
    op.create_index(op.f('ix_feedback_created_at'), 'feedback', ['created_at'])
    op.create_index(op.f('ix_feedback_sentiment'), 'feedback', ['sentiment'])
    op.create_index(op.f('ix_feedback_email_sent'), 'feedback', ['email_sent'])


def downgrade() -> None:
    """Drop feedback table"""
    op.drop_index(op.f('ix_feedback_email_sent'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_sentiment'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_created_at'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_email'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_feedback_id'), table_name='feedback')
    op.drop_table('feedback')

