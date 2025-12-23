"""Add task indexes for query optimization

Revision ID: 003
Revises: 002
Create Date: 2025-01-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add composite indexes and GIN index for task queries"""
    
    # Composite index for common task listing queries (status + created_at)
    # This optimizes queries like: SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at DESC
    op.create_index(
        'ix_tasks_status_created_at',
        'tasks',
        ['status', 'created_at'],
        unique=False
    )
    
    # Composite index for task type filtering (task_type + status)
    # This optimizes queries like: SELECT * FROM tasks WHERE task_type = 'security_scan' AND status = 'completed'
    op.create_index(
        'ix_tasks_task_type_status',
        'tasks',
        ['task_type', 'status'],
        unique=False
    )
    
    # Note: created_by column doesn't exist in tasks table schema
    # If needed, add created_by column in a future migration before creating this index
    # Composite index for user task queries (created_by + created_at) - REMOVED
    # This would optimize queries like: SELECT * FROM tasks WHERE created_by = 'user123' ORDER BY created_at DESC
    # op.create_index(
    #     'ix_tasks_created_by_created_at',
    #     'tasks',
    #     ['created_by', 'created_at'],
    #     unique=False
    # )
    
    # GIN index for JSONB queries on execution_metadata
    # This optimizes queries like: SELECT * FROM tasks WHERE execution_metadata @> '{"prediction": {...}}'
    # Note: GIN indexes are only available in PostgreSQL
    try:
        op.create_index(
            'ix_tasks_execution_metadata_gin',
            'tasks',
            ['execution_metadata'],
            postgresql_using='gin',
            unique=False
        )
    except Exception:
        # If PostgreSQL-specific features not available, skip GIN index
        # This allows the migration to work with other databases
        pass
    
    # Index for priority-based queries
    op.create_index(
        'ix_tasks_priority',
        'tasks',
        ['priority'],
        unique=False
    )
    
    # Index for completed_at queries (for analytics)
    op.create_index(
        'ix_tasks_completed_at',
        'tasks',
        ['completed_at'],
        unique=False
    )


def downgrade() -> None:
    """Remove all added indexes"""
    try:
        op.drop_index('ix_tasks_execution_metadata_gin', table_name='tasks')
    except Exception:
        pass
    
    op.drop_index('ix_tasks_completed_at', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')
    # op.drop_index('ix_tasks_created_by_created_at', table_name='tasks')  # Index doesn't exist
    op.drop_index('ix_tasks_task_type_status', table_name='tasks')
    op.drop_index('ix_tasks_status_created_at', table_name='tasks')

