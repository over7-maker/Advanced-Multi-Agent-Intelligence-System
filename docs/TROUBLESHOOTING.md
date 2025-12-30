# AMAS Troubleshooting Guide

## Common Issues and Solutions

### Database Issues

#### PostgreSQL Connection Failed

**Symptoms**:
- `ERROR: Database initialization failed`
- `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions**:
1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   # or
   systemctl status postgresql
   ```

2. Verify connection string:
   ```bash
   echo $DATABASE_URL
   # Should be: postgresql://user:password@host:port/database
   ```

3. Test connection manually:
   ```bash
   docker-compose exec postgres psql -U amas -d amas -c "SELECT 1"
   ```

4. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

5. Reset database (CAUTION: deletes data):
   ```bash
   docker-compose down -v
   docker-compose up -d postgres
   ```

#### Redis Connection Failed

**Symptoms**:
- `WARNING: Redis initialization failed: Authentication required`
- `redis.exceptions.AuthenticationError`

**Solutions**:
1. Check Redis password in environment:
   ```bash
   echo $REDIS_PASSWORD
   ```

2. Verify Redis URL format:
   ```bash
   # Should be: redis://:password@host:port/db
   echo $REDIS_URL
   ```

3. Test Redis connection:
   ```bash
   docker-compose exec redis redis-cli -a your_password ping
   ```

4. Check Redis logs:
   ```bash
   docker-compose logs redis
   ```

#### Neo4j Connection Failed

**Symptoms**:
- `WARNING: Neo4j connection failed`
- `neo4j.exceptions.AuthError`

**Solutions**:
1. Check Neo4j credentials:
   ```bash
   echo $NEO4J_PASSWORD
   ```

2. Test Neo4j connection:
   ```bash
   docker-compose exec neo4j cypher-shell -u neo4j -p your_password "RETURN 1"
   ```

3. Reset Neo4j password:
   ```bash
   docker-compose exec neo4j neo4j-admin set-initial-password your_new_password
   ```

### API Issues

#### 404 Not Found Errors

**Symptoms**:
- `404 Not Found` for API endpoints
- Frontend can't connect to backend

**Solutions**:
1. Check if backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verify API base URL in frontend:
   ```bash
   # Check frontend/.env
   cat frontend/.env | grep VITE_API_URL
   ```

3. Check CORS configuration:
   ```python
   # src/amas/api/main.py
   # Ensure frontend URL is in allow_origins
   ```

4. Check nginx configuration (if using):
   ```bash
   docker-compose logs nginx
   ```

#### Authentication Errors

**Symptoms**:
- `401 Unauthorized`
- `403 Forbidden`

**Solutions**:
1. Verify JWT token:
   ```bash
   # Decode token (use jwt.io)
   # Check expiration time
   ```

2. Check secret key:
   ```bash
   echo $SECRET_KEY
   echo $JWT_SECRET_KEY
   ```

3. Verify user exists:
   ```bash
   docker-compose exec postgres psql -U amas -d amas -c "SELECT * FROM users;"
   ```

4. Check token expiration:
   - Default: 3600 seconds (1 hour)
   - Use refresh token to get new access token

### Agent Issues

#### Agent Not Responding

**Symptoms**:
- Task stuck in "pending" status
- Agent execution timeout

**Solutions**:
1. Check agent status:
   ```bash
   curl http://localhost:8000/api/v1/agents/security_expert
   ```

2. Check agent logs:
   ```bash
   docker-compose logs amas-backend | grep "security_expert"
   ```

3. Verify AI provider connectivity:
   ```bash
   curl http://localhost:8000/api/v1/testing/providers
   ```

4. Check agent registry:
   ```python
   # Verify agent is registered in orchestrator
   ```

#### Agent Communication Failed

**Symptoms**:
- `ERROR: Agent communication failed`
- Events not being delivered

**Solutions**:
1. Check Event Bus status:
   ```bash
   # Check Redis connection (Event Bus uses Redis)
   docker-compose exec redis redis-cli ping
   ```

2. Verify Shared Context:
   ```python
   # Check if SharedContext is initialized
   ```

3. Check agent communication logs:
   ```bash
   docker-compose logs amas-backend | grep "communication"
   ```

### Performance Issues

#### Slow API Responses

**Symptoms**:
- API response time > 500ms
- Timeout errors

**Solutions**:
1. Check database query performance:
   ```bash
   docker-compose exec postgres psql -U amas -d amas -c "SELECT * FROM pg_stat_activity;"
   ```

2. Check cache hit rate:
   ```bash
   docker-compose exec redis redis-cli INFO stats | grep keyspace
   ```

3. Check system resources:
   ```bash
   docker stats
   # or
   kubectl top pods -n amas-production
   ```

4. Optimize database queries:
   - Add indexes
   - Review slow query log
   - Optimize connection pool

#### High Memory Usage

**Symptoms**:
- Out of memory errors
- Pods being killed

**Solutions**:
1. Check memory usage:
   ```bash
   docker stats
   # or
   kubectl top pods -n amas-production
   ```

2. Increase memory limits:
   ```yaml
   # docker-compose.prod.yml or k8s/deployment.yaml
   resources:
     limits:
       memory: 4Gi  # Increase if needed
   ```

3. Check for memory leaks:
   - Review application logs
   - Use memory profiler
   - Check for unclosed connections

### Deployment Issues

#### Docker Build Fails

**Symptoms**:
- `ERROR: failed to build`
- Dependency installation fails

**Solutions**:
1. Check Dockerfile:
   ```bash
   cat Dockerfile
   ```

2. Clear Docker cache:
   ```bash
   docker system prune -a
   ```

3. Build with no cache:
   ```bash
   docker build --no-cache -t amas-backend:latest .
   ```

4. Check requirements.txt:
   ```bash
   pip install -r requirements.txt --dry-run
   ```

#### Kubernetes Deployment Fails

**Symptoms**:
- Pods in `CrashLoopBackOff`
- Deployment not progressing

**Solutions**:
1. Check pod status:
   ```bash
   kubectl describe pod <pod-name> -n amas-production
   ```

2. Check pod logs:
   ```bash
   kubectl logs <pod-name> -n amas-production
   ```

3. Check events:
   ```bash
   kubectl get events -n amas-production --sort-by='.lastTimestamp'
   ```

4. Verify secrets:
   ```bash
   kubectl get secret amas-secrets -n amas-production -o yaml
   ```

5. Check resource limits:
   ```bash
   kubectl describe pod <pod-name> -n amas-production | grep -A 5 "Limits"
   ```

### Monitoring Issues

#### Prometheus Not Collecting Metrics

**Symptoms**:
- No metrics in Prometheus
- Grafana dashboards empty

**Solutions**:
1. Check Prometheus targets:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

2. Verify service discovery:
   ```bash
   # Check prometheus.yml configuration
   cat monitoring/prometheus/prometheus.yml
   ```

3. Check scrape endpoints:
   ```bash
   curl http://localhost:8000/metrics
   ```

4. Verify ServiceMonitor (if using):
   ```bash
   kubectl get servicemonitor -n amas-production
   ```

#### Grafana Not Loading Dashboards

**Symptoms**:
- Dashboards not appearing
- "No data" in panels

**Solutions**:
1. Check Grafana datasource:
   ```bash
   curl http://localhost:3001/api/datasources
   ```

2. Verify Prometheus connection:
   ```bash
   # In Grafana UI: Configuration > Data Sources > Test
   ```

3. Check dashboard provisioning:
   ```bash
   ls monitoring/grafana/dashboards/
   ```

4. Restart Grafana:
   ```bash
   docker-compose restart grafana
   ```

### Frontend Issues

#### Frontend Not Loading

**Symptoms**:
- Blank page
- 404 errors for assets

**Solutions**:
1. Check if frontend is built:
   ```bash
   ls frontend/dist/
   ```

2. Rebuild frontend:
   ```bash
   cd frontend
   npm run build:prod
   ```

3. Check nginx configuration:
   ```bash
   docker-compose logs nginx
   ```

4. Verify static file serving:
   ```bash
   curl http://localhost/
   ```

#### WebSocket Connection Failed

**Symptoms**:
- Real-time updates not working
- WebSocket errors in console

**Solutions**:
1. Check WebSocket endpoint:
   ```bash
   curl http://localhost:8000/ws
   ```

2. Verify nginx WebSocket configuration:
   ```nginx
   # nginx/nginx.conf
   location /ws {
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

3. Check CORS settings:
   ```python
   # src/amas/api/main.py
   # Ensure WebSocket origin is allowed
   ```

## Diagnostic Commands

### System Health Check

```bash
# Complete health check script
#!/bin/bash

echo "=== AMAS Health Check ==="

# Backend
echo "Backend Health:"
curl -s http://localhost:8000/health | jq .

# Databases
echo -e "\nPostgreSQL:"
docker-compose exec -T postgres pg_isready -U amas

echo -e "\nRedis:"
docker-compose exec -T redis redis-cli ping

echo -e "\nNeo4j:"
docker-compose exec -T neo4j cypher-shell -u neo4j -p password "RETURN 1" || echo "Neo4j not responding"

# Services
echo -e "\nService Status:"
docker-compose ps

# Resources
echo -e "\nResource Usage:"
docker stats --no-stream
```

### Log Analysis

```bash
# Search for errors
docker-compose logs amas-backend | grep -i error

# Search for warnings
docker-compose logs amas-backend | grep -i warning

# Last 100 lines
docker-compose logs --tail=100 amas-backend

# Follow logs
docker-compose logs -f amas-backend
```

### Performance Analysis

```bash
# Database query analysis
docker-compose exec postgres psql -U amas -d amas -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
"

# Redis memory usage
docker-compose exec redis redis-cli INFO memory

# System metrics
docker stats --no-stream
```

## Getting Help

### Logs to Collect

When reporting issues, collect:

1. **Application logs**:
   ```bash
   docker-compose logs amas-backend > amas-backend.log
   ```

2. **System logs**:
   ```bash
   docker-compose logs > all-services.log
   ```

3. **Configuration**:
   ```bash
   # .env file (remove secrets)
   cat .env > config.txt
   ```

4. **Health check output**:
   ```bash
   curl http://localhost:8000/health/detailed > health.json
   ```

### Support Channels

- **GitHub Issues**: https://github.com/your-org/amas/issues
- **Documentation**: https://docs.amas.example.com
- **Community Forum**: https://forum.amas.example.com

## Prevention

### Best Practices

1. **Regular Backups**:
   - Set up automated database backups
   - Test restore procedures regularly

2. **Monitoring**:
   - Set up alerting for critical metrics
   - Review dashboards regularly

3. **Updates**:
   - Keep dependencies updated
   - Apply security patches promptly

4. **Testing**:
   - Run tests before deployment
   - Test in staging before production

5. **Documentation**:
   - Document all configuration changes
   - Keep runbooks updated

