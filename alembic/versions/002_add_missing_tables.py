# alembic/versions/002_add_missing_tables.py
"""Add missing tables for complete AMAS schema

Revision ID: 002
Revises: 001
Create Date: 2025-01-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add missing 8 tables for complete AMAS schema"""
    
    # Task Executions table
    op.create_table(
        'task_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('execution_id', sa.String(255), nullable=False),
        sa.Column('task_id', sa.String(255), nullable=False),
        sa.Column('agent_id', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Numeric(10, 2), nullable=True),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error_details', postgresql.JSONB(), nullable=True),
        sa.Column('quality_score', sa.Numeric(5, 4), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('execution_id')
    )
    op.create_index(op.f('ix_task_executions_task_id'), 'task_executions', ['task_id'])
    op.create_index(op.f('ix_task_executions_agent_id'), 'task_executions', ['agent_id'])
    op.create_index(op.f('ix_task_executions_status'), 'task_executions', ['status'])
    
    # Integrations table
    op.create_table(
        'integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('platform', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('credentials', postgresql.JSONB(), nullable=True),
        sa.Column('configuration', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('sync_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('integration_id')
    )
    op.create_index(op.f('ix_integrations_user_id'), 'integrations', ['user_id'])
    op.create_index(op.f('ix_integrations_platform'), 'integrations', ['platform'])
    op.create_index(op.f('ix_integrations_status'), 'integrations', ['status'])
    
    # ML Models table
    op.create_table(
        'ml_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.String(255), nullable=False),
        sa.Column('model_type', sa.String(100), nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='training'),
        sa.Column('training_data_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('accuracy', sa.Numeric(5, 4), nullable=True),
        sa.Column('model_config', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('model_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_id')
    )
    op.create_index(op.f('ix_ml_models_model_type'), 'ml_models', ['model_type'])
    op.create_index(op.f('ix_ml_models_status'), 'ml_models', ['status'])
    
    # ML Training Data table
    op.create_table(
        'ml_training_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_id', sa.String(255), nullable=False),
        sa.Column('model_type', sa.String(100), nullable=False),
        sa.Column('features', postgresql.JSONB(), nullable=False),
        sa.Column('label', postgresql.JSONB(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('data_id')
    )
    op.create_index(op.f('ix_ml_training_data_model_type'), 'ml_training_data', ['model_type'])
    op.create_index(op.f('ix_ml_training_data_created_at'), 'ml_training_data', ['created_at'])
    
    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key_id', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('key_prefix', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('permissions', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_id')
    )
    op.create_index(op.f('ix_api_keys_user_id'), 'api_keys', ['user_id'])
    op.create_index(op.f('ix_api_keys_key_prefix'), 'api_keys', ['key_prefix'])
    op.create_index(op.f('ix_api_keys_is_active'), 'api_keys', ['is_active'])
    
    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('log_id', sa.String(255), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('log_id')
    )
    op.create_index(op.f('ix_audit_logs_event_type'), 'audit_logs', ['event_type'])
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'])
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'])
    
    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notification_id', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('data', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('read', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('notification_id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'])
    op.create_index(op.f('ix_notifications_read'), 'notifications', ['read'])
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'])
    
    # System Config table
    op.create_table(
        'system_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_key', sa.String(255), nullable=False),
        sa.Column('config_value', postgresql.JSONB(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_key')
    )
    op.create_index(op.f('ix_system_config_category'), 'system_config', ['category'])
    
    # Add execution_metadata column to tasks table if it doesn't exist
    try:
        op.add_column('tasks', sa.Column('execution_metadata', postgresql.JSONB(), nullable=True))
        op.add_column('tasks', sa.Column('started_at', sa.DateTime(), nullable=True))
        op.add_column('tasks', sa.Column('parameters', postgresql.JSONB(), nullable=True))
    except Exception:
        # Column might already exist
        pass

def downgrade() -> None:
    """Drop all added tables"""
    op.drop_index(op.f('ix_system_config_category'), table_name='system_config')
    op.drop_table('system_config')
    
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
    
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_event_type'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index(op.f('ix_api_keys_is_active'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_key_prefix'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_user_id'), table_name='api_keys')
    op.drop_table('api_keys')
    
    op.drop_index(op.f('ix_ml_training_data_created_at'), table_name='ml_training_data')
    op.drop_index(op.f('ix_ml_training_data_model_type'), table_name='ml_training_data')
    op.drop_table('ml_training_data')
    
    op.drop_index(op.f('ix_ml_models_status'), table_name='ml_models')
    op.drop_index(op.f('ix_ml_models_model_type'), table_name='ml_models')
    op.drop_table('ml_models')
    
    op.drop_index(op.f('ix_integrations_status'), table_name='integrations')
    op.drop_index(op.f('ix_integrations_platform'), table_name='integrations')
    op.drop_index(op.f('ix_integrations_user_id'), table_name='integrations')
    op.drop_table('integrations')
    
    op.drop_index(op.f('ix_task_executions_status'), table_name='task_executions')
    op.drop_index(op.f('ix_task_executions_agent_id'), table_name='task_executions')
    op.drop_index(op.f('ix_task_executions_task_id'), table_name='task_executions')
    op.drop_table('task_executions')
    
    # Remove added columns from tasks table
    try:
        op.drop_column('tasks', 'parameters')
        op.drop_column('tasks', 'started_at')
        op.drop_column('tasks', 'execution_metadata')
    except Exception:
        pass

