# AMAS Production Deployment Checklist

## Pre-Deployment (1-2 weeks before)

### 1. Infrastructure Preparation

#### 1.1 Server Setup
- [ ] Provision production servers (minimum specs: 8 vCPU, 32GB RAM, 500GB SSD)
- [ ] Install Docker (version 24.0+)
- [ ] Install Docker Compose (version 2.20+)
- [ ] Configure firewall rules
  - [ ] Allow port 80 (HTTP)
  - [ ] Allow port 443 (HTTPS)
  - [ ] Allow port 22 (SSH - restricted IPs only)
  - [ ] Block all other ports from external access
- [ ] Set up SSH key-based authentication
- [ ] Disable password authentication
- [ ] Configure automatic security updates

#### 1.2 Domain & DNS
- [ ] Register domain name
- [ ] Configure DNS records
  - [ ] A record for main domain → server IP
  - [ ] A record for www → server IP
  - [ ] A record for api → server IP
  - [ ] A record for monitoring → server IP
- [ ] SSL certificate obtained (Let's Encrypt or commercial)
- [ ] Configure SSL auto-renewal

#### 1.3 Monitoring & Alerting
- [ ] Set up monitoring dashboards
- [ ] Configure alert rules
- [ ] Set up Slack/email notifications
- [ ] Configure on-call schedule
- [ ] Test alert delivery

### 2. Security Configuration

#### 2.1 Secrets Management
- [ ] Generate strong SECRET_KEY (32+ chars)
- [ ] Generate strong JWT_SECRET (32+ chars)
- [ ] Generate strong database passwords
- [ ] Generate strong Redis password
- [ ] Generate strong Neo4j password
- [ ] Store all secrets in secure vault (AWS Secrets Manager / HashiCorp Vault)
- [ ] Never commit secrets to Git

#### 2.2 AI Provider API Keys
- [ ] OpenAI API key configured
- [ ] Anthropic API key configured
- [ ] Google AI API key configured
- [ ] Groq API key configured
- [ ] DeepSeek API key configured
- [ ] Cohere API key configured
- [ ] Mistral API key configured
- [ ] Together API key configured
- [ ] Perplexity API key configured
- [ ] Fireworks API key configured
- [ ] Replicate API key configured
- [ ] HuggingFace API key configured
- [ ] AI21 API key configured
- [ ] Aleph Alpha API key configured
- [ ] Writer API key configured
- [ ] Moonshot API key configured
- [ ] Set spending limits on all providers
- [ ] Configure rate limiting

#### 2.3 Integration Credentials
- [ ] GitHub token generated (if using GitHub integration)
- [ ] Slack bot token generated (if using Slack integration)
- [ ] Slack signing secret configured
- [ ] N8N base URL and API key configured
- [ ] Other integration credentials as needed

#### 2.4 Security Hardening
- [ ] Enable HTTPS only (redirect HTTP to HTTPS)
- [ ] Configure HSTS headers
- [ ] Set up Content Security Policy (CSP)
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up fail2ban or similar
- [ ] Configure regular security scans

### 3. Database Setup

#### 3.1 PostgreSQL
- [ ] Database created (name: amas)
- [ ] User created with strong password
- [ ] Connection pooling configured
- [ ] Backup strategy implemented
  - [ ] Daily automated backups
  - [ ] Weekly full backups
  - [ ] Off-site backup storage (S3/GCS)
  - [ ] Backup retention policy (30 days)
  - [ ] Backup restoration tested
- [ ] Database indexes optimized
- [ ] Query performance tuned

#### 3.2 Redis
- [ ] Redis password set
- [ ] Persistence enabled (AOF + RDB)
- [ ] Memory limit configured (maxmemory)
- [ ] Eviction policy set (allkeys-lru)
- [ ] Backup configured

#### 3.3 Neo4j (Optional)
- [ ] Neo4j password set
- [ ] Memory configured (heap + page cache)
- [ ] Indexes created
- [ ] Backup configured

### 4. Application Configuration

#### 4.1 Environment Variables
- [ ] Copy `.env.production.example` to `.env.production`
- [ ] Update all `CHANGE_THIS` placeholders
- [ ] Verify all required variables are set
- [ ] Test environment file loading

#### 4.2 CORS Configuration
- [ ] Update CORS_ORIGINS with production domain(s)
- [ ] Remove development origins
- [ ] Test CORS from production domain

#### 4.3 Logging
- [ ] Log level set to INFO or WARNING
- [ ] JSON logging enabled
- [ ] Log rotation configured
- [ ] Log aggregation set up (Loki)
- [ ] Log retention policy defined

### 5. Code Preparation

#### 5.1 Testing
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] End-to-end tests passing
- [ ] Code coverage > 80%
- [ ] Performance tests passing
- [ ] Load tests passing

#### 5.2 Code Quality
- [ ] Code reviewed by team
- [ ] No critical security vulnerabilities (run safety check)
- [ ] No high-priority bugs
- [ ] Dependencies up to date
- [ ] Dependency vulnerabilities resolved

#### 5.3 Documentation
- [ ] README.md updated
- [ ] API documentation complete
- [ ] Deployment documentation reviewed
- [ ] Runbook created for common issues
- [ ] Architecture diagrams updated

## Deployment Day

### 6. Pre-Deployment Steps

#### 6.1 Communication
- [ ] Notify team of deployment window
- [ ] Notify users of potential downtime (if applicable)
- [ ] Have rollback plan ready
- [ ] Have team on standby

#### 6.2 Final Checks
- [ ] Run pre-flight checks script
- [ ] Verify server resources available
- [ ] Verify SSL certificates valid
- [ ] Verify DNS propagation complete
- [ ] Test database connectivity
- [ ] Test Redis connectivity

### 7. Deployment Execution

#### 7.1 Backup
```
# Create backup before deployment
./scripts/backup.sh
```
- [ ] Database backup completed
- [ ] Backup verified

#### 7.2 Build & Deploy
```
# Deploy to production
./scripts/deploy-production.sh --build
```
- [ ] Docker images built successfully
- [ ] Containers started successfully
- [ ] Health checks passing

#### 7.3 Database Migration
```
# Run migrations
docker-compose -f docker-compose.prod.yml exec amas-backend alembic upgrade head
```
- [ ] Migrations completed successfully
- [ ] Database schema verified

#### 7.4 Verification
- [ ] API responding (http://your-domain.com/health)
- [ ] Frontend loading correctly
- [ ] User authentication working
- [ ] Task creation working
- [ ] Task execution working
- [ ] Integrations working
- [ ] Monitoring dashboards showing data

### 8. Post-Deployment

#### 8.1 Monitoring
- [ ] Check Grafana dashboards
- [ ] Verify metrics collection
- [ ] Check for errors in logs
- [ ] Monitor resource usage (CPU, memory, disk)
- [ ] Monitor response times
- [ ] Monitor error rates

#### 8.2 Smoke Tests
- [ ] Create test user account
- [ ] Create test task
- [ ] Execute test task
- [ ] Verify results
- [ ] Test integration triggers
- [ ] Test API endpoints
- [ ] Test WebSocket connection

#### 8.3 Performance
- [ ] Check API response times (< 200ms p95)
- [ ] Check database query times (< 50ms p95)
- [ ] Check cache hit rate (> 80%)
- [ ] Monitor system load
- [ ] Check for memory leaks

#### 8.4 Documentation
- [ ] Update deployment log
- [ ] Document any issues encountered
- [ ] Document any configuration changes
- [ ] Update version in Git (tag release)

## Day 1-7 Post-Deployment

### 9. Continuous Monitoring

#### 9.1 Daily Checks
- [ ] Review error logs
- [ ] Check system metrics
- [ ] Verify backups completed
- [ ] Monitor cost/usage of AI providers
- [ ] Check for security alerts

#### 9.2 Weekly Review
- [ ] Performance trends analysis
- [ ] Cost analysis
- [ ] User feedback review
- [ ] Plan optimizations

## Emergency Procedures

### 10. Rollback Plan

If deployment fails:

```
# Rollback to previous version
./scripts/deploy-production.sh --rollback <backup-file>
```

Steps:
1. Stop current containers
2. Restore database from backup
3. Deploy previous version
4. Verify rollback successful
5. Notify team
6. Investigate issue

### 11. Common Issues & Solutions

#### Issue: Database connection fails
```
# Check database is running
docker ps | grep postgres

# Check database logs
docker logs amas-postgres

# Verify credentials
docker exec -it amas-postgres psql -U amas -d amas
```

#### Issue: Redis connection fails
```
# Check Redis is running
docker ps | grep redis

# Test connection
docker exec -it amas-redis redis-cli ping
```

#### Issue: High memory usage
```
# Check container memory
docker stats

# Restart containers if needed
docker-compose -f docker-compose.prod.yml restart amas-backend
```

#### Issue: High CPU usage
- Check for infinite loops in logs
- Review recent deployments
- Scale horizontally if needed

## Success Criteria

Deployment is considered successful when:

- [ ] All services are running
- [ ] All health checks passing
- [ ] API response time < 200ms (p95)
- [ ] Error rate < 0.1%
- [ ] No critical alerts
- [ ] Monitoring dashboards showing data
- [ ] Users can successfully use the application
- [ ] No data loss occurred

## Post-Launch Optimization (Week 2+)

### 12. Performance Tuning
- [ ] Analyze slow queries
- [ ] Optimize database indexes
- [ ] Tune cache TTLs
- [ ] Review and optimize AI provider usage
- [ ] Set up CDN for static assets

### 13. Cost Optimization
- [ ] Review AI provider costs
- [ ] Optimize unnecessary API calls
- [ ] Review infrastructure costs
- [ ] Implement cost alerts

### 14. Security Audit
- [ ] Penetration testing
- [ ] Security scan results review
- [ ] Access logs review
- [ ] Update security policies

## Maintenance Schedule

### Daily
- Automated backups
- Log review
- Metrics review

### Weekly
- Security updates check
- Performance review
- Cost review

### Monthly
- Full security audit
- Disaster recovery test
- Capacity planning review

### Quarterly
- Major dependency updates
- Architecture review
- Security penetration test

---

## Emergency Contacts

**On-Call Engineer**: [Your contact]
**DevOps Lead**: [Your contact]
**Security Lead**: [Your contact]
**Product Owner**: [Your contact]

## Important URLs

- **Production**: https://your-domain.com
- **API**: https://api.your-domain.com
- **Monitoring**: https://monitoring.your-domain.com
- **Grafana**: https://monitoring.your-domain.com
- **Jaeger**: https://tracing.your-domain.com

---

Last Updated: $(date)
Version: 1.0.0

