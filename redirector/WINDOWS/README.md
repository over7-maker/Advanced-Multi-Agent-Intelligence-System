# Windows Backend API v4.0 - Production Final Edition

**Enterprise-Grade Data Collection & Storage System for L4 Redirector**

[![Version](https://img.shields.io/badge/version-4.0.0--final-blue.svg)](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System)
[![Python](https://img.shields.io/badge/python-3.12+-green.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-14+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 🎯 Overview

Production-ready backend API for collecting, storing, and analyzing data from the L4 Redirector system running on Ubuntu VPS. Optimized for Windows Server 2019/2022 with enterprise features including connection pooling, batch operations, and comprehensive monitoring.

## ✨ Features

### 🚀 Core Capabilities
- **8 Data Stream Endpoints** - Real-time ingestion from L4 Redirector
- **PostgreSQL Connection Pooling** - Efficient database connections (10-50 pool)
- **Batch Insert Optimization** - 100x faster than individual inserts
- **Token Authentication** - Timing-attack resistant security
- **Memory-Efficient Streaming** - Handles high-throughput scenarios
- **Comprehensive Error Handling** - Production-grade resilience
- **Health Monitoring** - Built-in diagnostics and metrics

### 📊 Data Streams

| Stream | Endpoint | Purpose |
|--------|----------|---------|  
| 1 | `/api/v1/web/{port}` | Web connection tracking |
| 2 | `/api/v1/l2n/{port}` | LocalToNet tunnel metrics |
| 3 | `/api/v1/errors/l2n/{port}` | Connection error logging |
| 4 | `/api/v1/performance/{port}` | Latency percentiles (P50/P95/P99) |
| 5 | `/api/v1/throughput/{port}` | Bandwidth statistics |
| 6 | `/api/v1/workers/status` | Worker health monitoring |
| 7 | `/api/v1/health/{port}` | Port health checks |
| 8 | `/api/v1/events/{port}` | Lifecycle event tracking |

## 📋 Requirements

### System Requirements
- **OS:** Windows Server 2019/2022 or Windows 10/11 Pro
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 50GB+ for database growth
- **Network:** Stable internet connection

### Software Dependencies
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/windows/)
- **NSSM** (optional) - [Download](https://nssm.cc/download) for Windows Service

## 🚀 Quick Start

### Automated Installation (Recommended)

```powershell
# Clone repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System/redirector/WINDOWS

# Run installer (as Administrator)
.\install.ps1

# Follow prompts and save generated credentials
```

### Manual Installation

1. **Install Prerequisites**
```powershell
# Install Python packages
pip install aiohttp asyncpg python-dotenv

# Verify PostgreSQL
psql --version
```

2. **Create Database**
```sql
-- Connect as postgres user
psql -U postgres

-- Create database and user
CREATE DATABASE redirector_db;
CREATE USER redirector_user WITH ENCRYPTED PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE redirector_db TO redirector_user;
\q

-- Load schema
psql -U redirector_user -d redirector_db -f database_schema.sql
```

3. **Configure Environment**
```powershell
# Edit config.env
notepad C:\backend_api\config.env

# Set these values:
DB_PASSWORD=your_secure_password
API_TOKEN=your_64_char_hex_token

# Generate token:
python -c "import secrets; print(secrets.token_hex(32))"
```

4. **Test Run**
```powershell
# Set environment
$env:DB_PASSWORD="your_password"
$env:API_TOKEN="your_token"

# Run API
python backend_api_v4.py
```

5. **Install as Service**
```powershell
# Using NSSM
nssm install BackendAPIv4 "C:\Python312\python.exe" "C:\backend_api\backend_api_v4.py"
nssm set BackendAPIv4 AppEnvironmentExtra :env_file=C:\backend_api\config.env
nssm start BackendAPIv4
```

## 🧪 Testing

### Run Test Suite
```powershell
.\test_api.ps1
```

### Manual Health Check
```powershell
# Test health endpoint (no auth required)
curl http://localhost:6921/health

# Expected response:
# {"status":"ok","version":"4.0.0-final","database":"connected",...}
```

### Test Authentication
```powershell
$TOKEN = (Get-Content config.env | Where-Object {$_ -match "API_TOKEN"}).Split("=")[1]

curl -H "Authorization: Bearer $TOKEN" `
     -Method POST `
     -Uri "http://localhost:6921/api/v1/web/8041" `
     -Body '[]' `
     -ContentType "application/json"
```

## 📊 Monitoring

### Check Service Status
```powershell
# Service status
Get-Service BackendAPIv4

# View logs
Get-Content C:\Logs\backend_api\backend_api_v4.log -Tail 50 -Wait
```

### Database Queries
```sql
-- Check data collection
SELECT 
    'web_connections' as table_name,
    COUNT(*) as row_count 
FROM web_connections
UNION ALL
SELECT 'l2n_tunnels', COUNT(*) FROM l2n_tunnels
UNION ALL
SELECT 'connection_errors', COUNT(*) FROM connection_errors;

-- Recent activity
SELECT * FROM web_connections 
WHERE timestamp > NOW() - INTERVAL '5 minutes'
ORDER BY timestamp DESC LIMIT 10;

-- Error rate analysis
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as error_count
FROM connection_errors
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_NAME` | No | `redirector_db` | Database name |
| `DB_USER` | No | `redirector_user` | Database user |
| `DB_PASSWORD` | **Yes** | - | Database password |
| `API_HOST` | No | `0.0.0.0` | API bind address |
| `API_PORT` | No | `6921` | API port |
| `API_TOKEN` | **Yes** | - | Authentication token |

### PostgreSQL Tuning (Production)

Add to `postgresql.conf`:
```
max_connections = 200
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
```

## 🔐 Security

### Checklist
- [ ] Strong database password (16+ characters)
- [ ] API token is 64 hex characters (256-bit)
- [ ] `config.env` has restricted permissions
- [ ] PostgreSQL only listens on localhost
- [ ] Firewall configured (port 6921 restricted to VPS IP)
- [ ] SSL/TLS enabled for production
- [ ] Regular database backups configured

### Firewall Configuration
```powershell
# Allow VPS IP only
New-NetFirewallRule -DisplayName "Backend API v4.0" `
                    -Direction Inbound `
                    -Protocol TCP `
                    -LocalPort 6921 `
                    -RemoteAddress YOUR_VPS_IP `
                    -Action Allow
```

## 📈 Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Insert latency | <10ms | Batch inserts |
| Connection pool | 10-50 | Auto-scaling |
| API response time | <50ms | Health checks |
| Database size | Monitor | Set up rotation |

## 🐛 Troubleshooting

### Common Issues

**Service won't start:**
```powershell
# Check logs
Get-Content C:\Logs\backend_api\backend_api_v4.log -Tail 100

# Verify environment
Get-Content C:\backend_api\config.env

# Test database connection
psql -U redirector_user -d redirector_db -h localhost
```

**Database connection errors:**
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# Verify credentials
psql -U redirector_user -d redirector_db -h localhost

# Check pg_hba.conf for localhost access
```

**High memory usage:**
- Reduce connection pool: Edit `DB_POOL_MAX` in code
- Enable connection pooling: Install pgBouncer
- Optimize queries: Add indexes for frequent queries

## 📚 API Documentation

### Authentication
All data stream endpoints require Bearer token authentication:
```
Authorization: Bearer YOUR_API_TOKEN
```

### Example Request
```powershell
$headers = @{
    "Authorization" = "Bearer $API_TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    timestamp = "2026-01-31T12:00:00Z"
    client_ip = "192.168.1.100"
    client_port = 54321
    bytes_in = 1024
    bytes_out = 2048
    duration_ms = 150
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:6921/api/v1/web/8041" `
                  -Method POST `
                  -Headers $headers `
                  -Body $body
```

### Response Format
```json
{
  "status": "success",
  "inserted": 1,
  "port": 8041
}
```

## 🔄 Integration with L4 Redirector

On your Ubuntu VPS, configure L4 Redirector:

```bash
# Edit /etc/l4-redirector/config.env
BACKEND_API_URL=http://YOUR_WINDOWS_IP:6921
BACKEND_API_TOKEN=your_64_char_token

# Restart redirector
sudo systemctl restart l4-redirector
```

## 📁 File Structure

```
C:\backend_api\
├── backend_api_v4.py       # Main application
├── config.env              # Configuration
├── database_schema.sql     # Database schema
├── install.ps1             # Installation script
└── test_api.ps1            # Test suite

C:\Logs\backend_api\
└── backend_api_v4.log      # Application logs
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- **Documentation:** [Wiki](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/wiki)
- **Email:** over7@su.edu.ye

## 📝 Changelog

### v4.0.0-final (2026-01-31)
- ✅ Production-ready release
- ✅ 8 data stream endpoints
- ✅ Batch insert optimization
- ✅ Connection pooling
- ✅ Comprehensive error handling
- ✅ Windows Service support
- ✅ Automated installation

---

**Version:** 4.0.0-final  
**Release Date:** January 31, 2026  
**Status:** Production Ready  
**Compatibility:** Works with L4 Redirector v4.0+
