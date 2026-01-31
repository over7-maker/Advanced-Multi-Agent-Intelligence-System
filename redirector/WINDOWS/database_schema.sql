-- Windows Backend API v4.0 Database Schema
-- PostgreSQL 14+

-- Stream 1: Web Connections
CREATE TABLE IF NOT EXISTS web_connections (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    port INTEGER NOT NULL,
    client_ip VARCHAR(45) NOT NULL,
    client_port INTEGER NOT NULL,
    bytes_in BIGINT DEFAULT 0,
    bytes_out BIGINT DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    worker_id VARCHAR(50),
    connection_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_web_conn_timestamp ON web_connections(timestamp);
CREATE INDEX idx_web_conn_port ON web_connections(port);
CREATE INDEX idx_web_conn_client_ip ON web_connections(client_ip);

-- Stream 2: L2N Tunnels
CREATE TABLE IF NOT EXISTS l2n_tunnels (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    port INTEGER NOT NULL,
    backend_ip VARCHAR(45) NOT NULL,
    backend_port INTEGER NOT NULL,
    duration_ms INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    worker_id VARCHAR(50),
    tunnel_status VARCHAR(20),
    localtonet_gateway VARCHAR(100),
    bytes_transferred BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_l2n_timestamp ON l2n_tunnels(timestamp);
CREATE INDEX idx_l2n_port ON l2n_tunnels(port);
CREATE INDEX idx_l2n_backend_ip ON l2n_tunnels(backend_ip);

-- Stream 3: Connection Errors
CREATE TABLE IF NOT EXISTS connection_errors (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    port INTEGER NOT NULL,
    error_type VARCHAR(50) NOT NULL,
    backend_ip VARCHAR(45),
    backend_port INTEGER,
    client_ip VARCHAR(45),
    client_port INTEGER,
    error_message TEXT,
    worker_id VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_errors_timestamp ON connection_errors(timestamp);
CREATE INDEX idx_errors_port ON connection_errors(port);
CREATE INDEX idx_errors_type ON connection_errors(error_type);

-- Stream 4: Performance Metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    port INTEGER NOT NULL,
    p50 INTEGER,
    p95 INTEGER,
    p99 INTEGER,
    min_latency INTEGER,
    max_latency INTEGER,
    sample_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_perf_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_perf_port ON performance_metrics(port);

-- Stream 5: Throughput Statistics
CREATE TABLE IF NOT EXISTS throughput_stats (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    port INTEGER NOT NULL,
    bytes_per_sec BIGINT,
    connections_per_sec NUMERIC(10,2),
    total_bytes_in BIGINT,
    total_bytes_out BIGINT,
    total_connections INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_throughput_timestamp ON throughput_stats(timestamp);
CREATE INDEX idx_throughput_port ON throughput_stats(port);

-- Stream 6: Worker Health
CREATE TABLE IF NOT EXISTS worker_health (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    worker_data JSONB NOT NULL,
    worker_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_worker_timestamp ON worker_health(timestamp);

-- Stream 7: Port Health
CREATE TABLE IF NOT EXISTS port_health (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    port INTEGER NOT NULL,
    tcp_status VARCHAR(20),
    tcp_latency_ms INTEGER,
    udp_status VARCHAR(20),
    uptime_sec BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_health_timestamp ON port_health(timestamp);
CREATE INDEX idx_health_port ON port_health(port);

-- Stream 8: Lifecycle Events
CREATE TABLE IF NOT EXISTS lifecycle_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    port INTEGER NOT NULL,
    events JSONB NOT NULL,
    event_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_timestamp ON lifecycle_events(timestamp);
CREATE INDEX idx_events_port ON lifecycle_events(port);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO redirector_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO redirector_user;
