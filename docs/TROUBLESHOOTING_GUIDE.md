# AMAS Troubleshooting Guide (Phase 7.4)

## Common Issues and Solutions

### Database Connection Issues

#### PostgreSQL Connection Failed

**Symptoms:**
- Error: `could not connect to server`
- Service won't start
- Database queries fail

**Solutions:**
1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Verify connection string:
   ```bash
   echo $DATABASE_URL
   ```

3. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

4. Test connection manually:
   ```bash
   psql -h localhost -U postgres -d amas
   ```

5. Reset PostgreSQL (if needed):
   ```bash
   docker-compose down postgres
   docker volume rm amas_postgres_data
   docker-compose up -d postgres
   ```

#### Redis Connection Failed

**Symptoms:**
- Cache operations fail
- `Connection refused` errors
- Redis commands timeout

**Solutions:**
1. Check Redis status:
   ```bash
   docker-compose ps redis
   redis-cli -h localhost -p 6379 ping
   ```

2. Verify password:
   ```bash
   redis-cli -h localhost -p 6379 -a $REDIS_PASSWORD ping
   ```

3. Check Redis logs:
   ```bash
   docker-compose logs redis
   ```

4. Clear Redis cache (if needed):
   ```bash
   redis-cli -h localhost -p 6379 -a $REDIS_PASSWORD FLUSHALL
   ```

#### Neo4j Connection Failed

**Symptoms:**
- Graph queries fail
- Neo4j driver errors
- Connection timeout

**Solutions:**
1. Check Neo4j status:
   ```bash
   docker-compose ps neo4j
   ```

2. Verify credentials:
   ```bash
   echo $NEO4J_PASSWORD
   ```

3. Test connection:
   ```bash
   cypher-shell -u neo4j -p $NEO4J_PASSWORD -a bolt://localhost:7687
   ```

4. Check Neo4j logs:
   ```bash
   docker-compose logs neo4j
   ```

### Application Issues

#### Service Won't Start

**Symptoms:**
- Container exits immediately
- Health checks fail
- Application errors on startup

**Solutions:**
1. Check application logs:
   ```bash
   docker-compose logs amas
   ```

2. Verify environment variables:
   ```bash
   docker-compose config | grep -A 20 amas:
   ```

3. Check for missing dependencies:
   ```bash
   docker-compose exec amas pip list
   ```

4. Verify database connections are ready:
   ```bash
   # Wait for databases to be healthy
   docker-compose up -d postgres redis neo4j
   sleep 10
   docker-compose up -d amas
   ```

#### API Returns 500 Errors

**Symptoms:**
- Internal server errors
- Task creation fails
- Agent execution errors

**Solutions:**
1. Check application logs:
   ```bash
   docker-compose logs -f amas | grep ERROR
   ```

2. Verify orchestrator status:
   ```bash
   curl http://localhost:8000/api/v1/system/orchestrator/status
   ```

3. Check database connectivity:
   ```bash
   docker-compose exec amas python -c "from src.database.connection import get_session; print('DB OK')"
   ```

4. Verify AI provider keys:
   ```bash
   docker-compose exec amas env | grep API_KEY
   ```

#### WebSocket Connection Fails

**Symptoms:**
- Real-time updates not working
- WebSocket connection refused
- Frontend can't connect

**Solutions:**
1. Check WebSocket endpoint:
   ```bash
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8000/ws
   ```

2. Verify Nginx WebSocket configuration:
   ```bash
   cat nginx/nginx.conf | grep -A 10 "location /ws"
   ```

3. Check WebSocket logs:
   ```bash
   docker-compose logs amas | grep websocket
   ```

4. Test WebSocket connection:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws');
   ws.onopen = () => console.log('Connected');
   ws.onerror = (e) => console.error('Error:', e);
   ```

### Performance Issues

#### Slow API Responses

**Symptoms:**
- API takes >1 second to respond
- Timeout errors
- High latency

**Solutions:**
1. Check database query performance:
   ```bash
   python scripts/performance_optimization.py --analyze
   ```

2. Monitor cache hit rate:
   ```bash
   redis-cli -h localhost -p 6379 INFO stats | grep keyspace
   ```

3. Check resource usage:
   ```bash
   docker stats
   ```

4. Optimize database:
   ```bash
   python scripts/performance_optimization.py --optimize-db
   ```

#### High Memory Usage

**Symptoms:**
- Containers using excessive memory
- Out of memory errors
- System slowdown

**Solutions:**
1. Check memory usage:
   ```bash
   docker stats --no-stream
   ```

2. Review resource limits in docker-compose.prod.yml

3. Restart services:
   ```bash
   docker-compose restart
   ```

4. Clear caches:
   ```bash
   redis-cli -h localhost -p 6379 -a $REDIS_PASSWORD FLUSHALL
   ```

#### Database Query Timeouts

**Symptoms:**
- Queries take >5 seconds
- Connection pool exhausted
- Timeout errors

**Solutions:**
1. Check active connections:
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   ```

2. Analyze slow queries:
   ```bash
   python scripts/performance_optimization.py --optimize-db
   ```

3. Increase connection pool size in configuration

4. Add database indexes:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
   CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
   ```

### Security Issues

#### Authentication Fails

**Symptoms:**
- Login returns 401
- JWT tokens invalid
- Session expired errors

**Solutions:**
1. Verify JWT secret:
   ```bash
   echo $JWT_SECRET_KEY
   ```

2. Check token expiration:
   ```bash
   # Tokens expire after 30 minutes by default
   ```

3. Verify user exists:
   ```sql
   SELECT * FROM users WHERE username = 'your_username';
   ```

4. Check authentication logs:
   ```bash
   docker-compose logs amas | grep auth
   ```

#### SSL Certificate Errors

**Symptoms:**
- HTTPS connection fails
- Certificate expired
- SSL handshake errors

**Solutions:**
1. Check certificate validity:
   ```bash
   openssl x509 -in nginx/ssl/fullchain.pem -noout -dates
   ```

2. Renew Let's Encrypt certificate:
   ```bash
   certbot renew
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
   docker-compose restart nginx
   ```

3. Verify Nginx SSL configuration:
   ```bash
   nginx -t -c nginx/nginx.conf
   ```

### Monitoring Issues

#### Prometheus Not Collecting Metrics

**Symptoms:**
- No metrics in Prometheus
- Grafana dashboards empty
- Metrics endpoint returns 404

**Solutions:**
1. Check Prometheus status:
   ```bash
   docker-compose ps prometheus
   curl http://localhost:9090/-/healthy
   ```

2. Verify scrape configuration:
   ```bash
   cat monitoring/prometheus.yml
   ```

3. Check target status:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

4. Restart Prometheus:
   ```bash
   docker-compose restart prometheus
   ```

#### Grafana Dashboards Not Loading

**Symptoms:**
- Dashboards show "No data"
- Prometheus data source fails
- Panels don't render

**Solutions:**
1. Verify Grafana data source:
   - Access Grafana: http://localhost:3001
   - Check data source configuration
   - Test connection to Prometheus

2. Check Prometheus connectivity:
   ```bash
   curl http://prometheus:9090/api/v1/query?query=up
   ```

3. Verify dashboard JSON files:
   ```bash
   ls -la monitoring/grafana/dashboards/
   ```

### Backup & Recovery Issues

#### Backup Fails

**Symptoms:**
- Backup script errors
- No backup files created
- Permission denied errors

**Solutions:**
1. Check backup directory permissions:
   ```bash
   ls -la backups/
   mkdir -p backups
   chmod 755 backups
   ```

2. Verify database credentials:
   ```bash
   echo $POSTGRES_PASSWORD
   ```

3. Test backup manually:
   ```bash
   python scripts/backup_database.py --backup-dir ./backups
   ```

4. Check disk space:
   ```bash
   df -h
   ```

#### Restore Fails

**Symptoms:**
- Restore script errors
- Database corruption
- Restore incomplete

**Solutions:**
1. Verify backup file exists:
   ```bash
   ls -lh backups/postgres_amas_*.sql.gz
   ```

2. Test backup file integrity:
   ```bash
   gunzip -t backups/postgres_amas_YYYYMMDD_HHMMSS.sql.gz
   ```

3. Create database backup before restore:
   ```bash
   python scripts/backup_database.py
   ```

4. Restore with drop existing (WARNING: Destructive):
   ```bash
   python scripts/restore_database.py backups/postgres_amas_YYYYMMDD_HHMMSS.sql.gz --drop-existing
   ```

## Diagnostic Commands

### System Health Check
```bash
# Check all services
docker-compose ps

# Check resource usage
docker stats --no-stream

# Check logs for errors
docker-compose logs --tail=100 | grep -i error

# Check disk space
df -h

# Check memory
free -h
```

### Database Health
```bash
# PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# Redis
docker-compose exec redis redis-cli ping

# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p $NEO4J_PASSWORD "RETURN 1"
```

### Application Health
```bash
# API health
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/v1/system/health

# Orchestrator status
curl http://localhost:8000/api/v1/system/orchestrator/status
```

## Getting Help

1. **Check Logs First**: Most issues can be diagnosed from logs
   ```bash
   docker-compose logs [service_name]
   ```

2. **Review Documentation**: 
   - `docs/PRODUCTION_DEPLOYMENT_GUIDE.md`
   - `docs/API_DOCUMENTATION.md`

3. **GitHub Issues**: Search existing issues or create new one

4. **Community Support**: Check project discussions

## Emergency Procedures

### Complete System Restart
```bash
# Stop all services
docker-compose down

# Start services in order
docker-compose up -d postgres redis neo4j
sleep 10
docker-compose up -d prometheus grafana
sleep 5
docker-compose up -d amas frontend nginx
```

### Database Recovery
```bash
# Stop application
docker-compose stop amas

# Restore from backup
python scripts/restore_database.py backups/postgres_amas_YYYYMMDD_HHMMSS.sql.gz

# Restart application
docker-compose start amas
```

### Reset Everything (WARNING: Destructive)
```bash
# Stop all services
docker-compose down

# Remove all volumes (WARNING: Data loss!)
docker volume rm $(docker volume ls -q | grep amas)

# Restart fresh
docker-compose up -d
```
