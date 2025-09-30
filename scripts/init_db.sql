-- AMAS Intelligence System Database Initialization Script

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS amas;

-- Use the database
\c amas;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    capabilities TEXT[],
    status VARCHAR(20) DEFAULT 'inactive',
    last_activity TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 2,
    status VARCHAR(20) DEFAULT 'pending',
    assigned_agent VARCHAR(50),
    parameters JSONB,
    result JSONB,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create workflows table
CREATE TABLE IF NOT EXISTS workflows (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50) NOT NULL,
    steps JSONB,
    status VARCHAR(20) DEFAULT 'inactive',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create workflow_executions table
CREATE TABLE IF NOT EXISTS workflow_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(50) UNIQUE NOT NULL,
    workflow_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'running',
    parameters JSONB,
    results JSONB,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    details TEXT,
    classification VARCHAR(20) DEFAULT 'system',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create intelligence_data table
CREATE TABLE IF NOT EXISTS intelligence_data (
    id SERIAL PRIMARY KEY,
    data_id VARCHAR(50) UNIQUE NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    source VARCHAR(100),
    content TEXT,
    metadata JSONB,
    classification VARCHAR(20) DEFAULT 'unclassified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create entities table
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) UNIQUE NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    attributes JSONB,
    relationships JSONB,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create relationships table
CREATE TABLE IF NOT EXISTS relationships (
    id SERIAL PRIMARY KEY,
    relationship_id VARCHAR(50) UNIQUE NOT NULL,
    source_entity_id VARCHAR(50) NOT NULL,
    target_entity_id VARCHAR(50) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    attributes JSONB,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(assigned_agent);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_intelligence_data_type ON intelligence_data(data_type);
CREATE INDEX IF NOT EXISTS idx_intelligence_data_classification ON intelligence_data(classification);
CREATE INDEX IF NOT EXISTS idx_intelligence_data_created ON intelligence_data(created_at);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_confidence ON entities(confidence_score);

CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_entity_id);

-- Insert default admin user
INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@amas.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8.8.8.8', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Insert default agents
INSERT INTO agents (agent_id, name, agent_type, capabilities, status) VALUES
('osint_001', 'OSINT Agent', 'osint', ARRAY['web_scraping', 'social_media_monitoring', 'news_aggregation', 'domain_analysis', 'email_analysis', 'social_network_analysis', 'threat_intelligence', 'dark_web_monitoring'], 'active'),
('investigation_001', 'Investigation Agent', 'investigation', ARRAY['link_analysis', 'entity_resolution', 'timeline_reconstruction', 'correlation_analysis', 'pattern_recognition'], 'active'),
('forensics_001', 'Forensics Agent', 'forensics', ARRAY['evidence_acquisition', 'file_analysis', 'timeline_analysis', 'metadata_extraction', 'hash_analysis', 'memory_analysis'], 'active'),
('data_analysis_001', 'Data Analysis Agent', 'data_analysis', ARRAY['statistical_analysis', 'predictive_modeling', 'pattern_recognition', 'anomaly_detection', 'data_visualization', 'trend_analysis'], 'active'),
('reverse_engineering_001', 'Reverse Engineering Agent', 'reverse_engineering', ARRAY['binary_analysis', 'malware_analysis', 'code_deobfuscation', 'protocol_analysis', 'firmware_analysis', 'network_analysis'], 'active'),
('metadata_001', 'Metadata Agent', 'metadata', ARRAY['exif_extraction', 'pdf_analysis', 'office_analysis', 'image_analysis', 'audio_analysis', 'video_analysis'], 'active'),
('reporting_001', 'Reporting Agent', 'reporting', ARRAY['report_generation', 'data_visualization', 'executive_summaries', 'threat_assessments', 'intelligence_briefs', 'dashboard_creation'], 'active'),
('technology_monitor_001', 'Technology Monitor Agent', 'technology_monitor', ARRAY['technology_trends', 'academic_papers', 'github_monitoring', 'patent_analysis', 'research_tracking', 'innovation_monitoring'], 'active')
ON CONFLICT (agent_id) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW active_agents AS
SELECT agent_id, name, agent_type, capabilities, last_activity
FROM agents 
WHERE status = 'active';

CREATE OR REPLACE VIEW recent_tasks AS
SELECT task_id, task_type, description, status, assigned_agent, created_at
FROM tasks 
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY created_at DESC;

CREATE OR REPLACE VIEW system_metrics AS
SELECT 
    (SELECT COUNT(*) FROM agents WHERE status = 'active') as active_agents,
    (SELECT COUNT(*) FROM tasks WHERE status = 'pending') as pending_tasks,
    (SELECT COUNT(*) FROM tasks WHERE status = 'in_progress') as active_tasks,
    (SELECT COUNT(*) FROM tasks WHERE status = 'completed') as completed_tasks,
    (SELECT COUNT(*) FROM audit_logs WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours') as daily_audit_events;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO amas;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO amas;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO amas;