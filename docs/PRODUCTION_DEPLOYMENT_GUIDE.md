# AMAS Production Deployment Guide (Phase 7.4)

## Overview

This guide provides step-by-step instructions for deploying AMAS to production with all security, performance, and reliability measures in place.

## Prerequisites

- Docker & Docker Compose installed
- PostgreSQL 15+, Redis 7+, Neo4j 5+
- SSL/TLS certificates (Let's Encrypt recommended)
- Domain name configured
- All 16 AI provider API keys
- Production secrets generated

## Step 1: Generate Production Secrets

```bash
# Generate secure passwords and secrets
python scripts/generate_production_secrets.py

# This creates:
# - config/production/.env.production
# - config/production/docker-compose.env
```

**⚠️ CRITICAL**: Store these secrets securely:
- Use a password manager
- Use a secrets vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- Never commit secrets to version control

## Step 2: Configure SSL/TLS Certificates

```bash
# Using Let's Encrypt (recommended)
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
```

## Step 3: Update Configuration Files

### Update nginx.conf
- Replace `your-domain.com` with your actual domain
- Ensure SSL certificates are in `nginx/ssl/`

### Update docker-compose.prod.yml
- All passwords use environment variables
- Resource limits configured
- Health checks enabled

## Step 4: Set Up Database Backups

```bash
# Create backup directory
mkdir -p backups

# Test backup
python scripts/backup_database.py

# Schedule daily backups (cron)
# Add to crontab:
0 2 * * * /path/to/scripts/backup_database.py --backup-dir /path/to/backups
```

## Step 5: Deploy Services

```bash
# Start production stack
docker-compose --env-file config/production/docker-compose.env -f docker-compose.prod.yml up -d

# Verify all services are healthy
docker-compose -f docker-compose.prod.yml ps
```

## Step 6: Verify Deployment

### Health Checks
```bash
# API health
curl https://your-domain.com/health

# System status
curl https://your-domain.com/api/v1/system/health

# Orchestrator status
curl https://your-domain.com/api/v1/system/orchestrator/status
```

### Monitor Logs
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs -f amas

# All services
docker-compose -f docker-compose.prod.yml logs -f
```

## Step 7: Performance Optimization

```bash
# Run performance analysis
python scripts/performance_optimization.py --analyze

# Optimize database
python scripts/performance_optimization.py --optimize-db

# Optimize cache
python scripts/performance_optimization.py --optimize-cache
```

## Security Checklist

- [ ] All default passwords changed
- [ ] SSL/TLS certificates installed and valid
- [ ] Security headers configured in Nginx
- [ ] Rate limiting enabled
- [ ] Firewall rules configured
- [ ] Secrets stored securely (not in code)
- [ ] Audit logging enabled
- [ ] Regular security scans scheduled

## Monitoring

### Prometheus
- Access: `https://monitoring.your-domain.com:9090`
- Metrics endpoint: `/metrics`

### Grafana
- Access: `https://monitoring.your-domain.com:3001`
- Default credentials: admin / (from GRAFANA_ADMIN_PASSWORD)

### Key Metrics to Monitor
- API response times (p95 < 200ms)
- Database query times (p95 < 50ms)
- Cache hit rate (>80%)
- Error rate (<0.1%)
- System resource usage (CPU, memory)

## Backup & Recovery

### Daily Backups
Backups run automatically via cron:
```bash
0 2 * * * python scripts/backup_database.py
```

### Manual Backup
```bash
python scripts/backup_database.py --backup-dir /path/to/backups
```

### Restore from Backup
```bash
python scripts/restore_database.py /path/to/backups/postgres_amas_YYYYMMDD_HHMMSS.sql.gz
```

## Troubleshooting

### Service Won't Start
1. Check logs: `docker-compose -f docker-compose.prod.yml logs [service]`
2. Verify environment variables are set
3. Check database connectivity
4. Verify SSL certificates exist

### Performance Issues
1. Check database query times
2. Monitor cache hit rates
3. Review resource limits
4. Run performance analysis script

### Security Issues
1. Review audit logs
2. Check for failed login attempts
3. Verify SSL certificates are valid
4. Review security scan results

## Maintenance

### Regular Tasks
- **Daily**: Monitor logs, check backups
- **Weekly**: Review performance metrics, optimize queries
- **Monthly**: Security scans, dependency updates
- **Quarterly**: Full security audit, disaster recovery test

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review documentation: `docs/`
- Check GitHub Issues: [Repository Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)

