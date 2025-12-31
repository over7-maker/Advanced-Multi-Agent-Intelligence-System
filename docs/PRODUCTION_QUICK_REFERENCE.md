# AMAS Production Quick Reference (Phase 7.4)

## Quick Commands

### Start Production Stack
```bash
# Generate secrets first (one-time)
python scripts/generate_production_secrets.py

# Start with production config
docker-compose --env-file config/production/docker-compose.env -f docker-compose.prod.yml up -d
```

### Stop Production Stack
```bash
docker-compose -f docker-compose.prod.yml down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f amas
```

### Health Checks
```bash
# API health
curl https://your-domain.com/health

# System status
curl https://your-domain.com/api/v1/system/health

# Orchestrator status
curl https://your-domain.com/api/v1/system/orchestrator/status
```

### Database Operations

#### Backup
```bash
python scripts/backup_database.py --backup-dir ./backups
```

#### Restore
```bash
python scripts/restore_database.py backups/postgres_amas_YYYYMMDD_HHMMSS.sql.gz
```

### Performance Optimization
```bash
# Analyze performance
python scripts/performance_optimization.py --analyze

# Optimize database
python scripts/performance_optimization.py --optimize-db

# Optimize cache
python scripts/performance_optimization.py --optimize-cache
```

### Monitoring

#### Prometheus
- URL: `http://localhost:9090`
- Metrics: `http://localhost:9090/metrics`

#### Grafana
- URL: `http://localhost:3001`
- Default user: `admin`
- Password: From `GRAFANA_ADMIN_PASSWORD` env var

### Service Management

#### Restart Service
```bash
docker-compose -f docker-compose.prod.yml restart [service_name]
```

#### Scale Service
```bash
docker-compose -f docker-compose.prod.yml up -d --scale amas=3
```

#### View Resource Usage
```bash
docker stats --no-stream
```

## Environment Variables

### Required for Production
- `POSTGRES_PASSWORD` - PostgreSQL password
- `REDIS_PASSWORD` - Redis password
- `NEO4J_PASSWORD` - Neo4j password
- `SECRET_KEY` - Application secret key
- `JWT_SECRET_KEY` - JWT signing key
- `GRAFANA_ADMIN_PASSWORD` - Grafana admin password

### AI Provider Keys (16 providers)
- `CEREBRAS_API_KEY`
- `NVIDIA_API_KEY`
- `GROQ2_API_KEY`
- `GROQAI_API_KEY`
- `DEEPSEEK_API_KEY`
- `CODESTRAL_API_KEY`
- `GLM_API_KEY`
- `GEMINI2_API_KEY`
- `GROK_API_KEY`
- `COHERE_API_KEY`
- `KIMI_API_KEY`
- `QWEN_API_KEY`
- `GPTOSS_API_KEY`
- `CHUTES_API_KEY`

## File Locations

### Configuration
- Production secrets: `config/production/.env.production`
- Docker Compose: `docker-compose.prod.yml`
- Nginx config: `nginx/nginx.conf`
- SSL certificates: `nginx/ssl/`

### Scripts
- Generate secrets: `scripts/generate_production_secrets.py`
- Backup: `scripts/backup_database.py`
- Restore: `scripts/restore_database.py`
- Performance: `scripts/performance_optimization.py`

### Documentation
- Deployment: `docs/PRODUCTION_DEPLOYMENT_GUIDE.md`
- API: `docs/API_DOCUMENTATION.md`
- Troubleshooting: `docs/TROUBLESHOOTING_GUIDE.md`

## Common Tasks

### Update Secrets
1. Generate new secrets: `python scripts/generate_production_secrets.py`
2. Update `config/production/.env.production`
3. Restart services: `docker-compose -f docker-compose.prod.yml restart`

### Renew SSL Certificate
```bash
certbot renew
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
docker-compose -f docker-compose.prod.yml restart nginx
```

### View Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Check Disk Space
```bash
df -h
docker system df
```

### Clean Up Old Backups
```bash
# Backups older than 30 days are automatically cleaned
# Manual cleanup:
find backups/ -name "*.sql.gz" -mtime +30 -delete
```

## Emergency Procedures

### Complete Restart
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Database Recovery
```bash
# Stop application
docker-compose -f docker-compose.prod.yml stop amas

# Restore backup
python scripts/restore_database.py backups/postgres_amas_YYYYMMDD_HHMMSS.sql.gz

# Restart
docker-compose -f docker-compose.prod.yml start amas
```

### Reset All (WARNING: Data Loss)
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

## Support

- **Documentation**: See `docs/` directory
- **Troubleshooting**: `docs/TROUBLESHOOTING_GUIDE.md`
- **Issues**: GitHub Issues
- **Logs**: `docker-compose -f docker-compose.prod.yml logs`

