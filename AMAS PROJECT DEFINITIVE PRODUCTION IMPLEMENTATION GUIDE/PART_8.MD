# **🎯 AMAS PROJECT: PART 8 - PRODUCTION DEPLOYMENT CONFIGURATION**
## **Docker, Kubernetes, CI/CD, Security & Infrastructure as Code**

---

## **PART 8: PRODUCTION DEPLOYMENT & INFRASTRUCTURE**

### **Step 8.1: Production Docker Configuration**

**File**: `Dockerfile` (PRODUCTION-READY - ENHANCE EXISTING)

```dockerfile
# Dockerfile (PRODUCTION-OPTIMIZED MULTI-STAGE BUILD)

# ============================================================================
# STAGE 1: Python Dependencies Builder
# ============================================================================
FROM python:3.11-slim as python-builder

WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: Frontend Builder
# ============================================================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# ============================================================================
# STAGE 3: Production Runtime
# ============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production \
    PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r amas && useradd -r -g amas amas

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Copy application code
COPY --chown=amas:amas src/ ./src/
COPY --chown=amas:amas scripts/ ./scripts/
COPY --chown=amas:amas alembic.ini ./
COPY --chown=amas:amas alembic/ ./alembic/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R amas:amas /app/logs /app/data

# Switch to non-root user
USER amas

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

***

### **Step 8.2: Docker Compose - Complete Stack**

**File**: `docker-compose.prod.yml` (PRODUCTION VERSION)

```yaml
# docker-compose.prod.yml (PRODUCTION STACK)
version: '3.8'

services:
  # ============================================================================
  # APPLICATION SERVICES
  # ============================================================================

  # AMAS Backend API
  amas-backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: amas-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      # Database
      - DATABASE_URL=postgresql://amas:${DB_PASSWORD}@postgres:5432/amas
      
      # Redis
      - REDIS_URL=redis://redis:6379/0
      
      # Neo4j (if using)
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      
      # AI Providers
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      
      # Security
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000}
      
      # Monitoring
      - JAEGER_ENDPOINT=jaeger:6831
      - OTLP_ENDPOINT=tempo:4317
      
      # Application
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - JSON_LOGS=true
      
    volumes:
      - amas-logs:/app/logs
      - amas-data:/app/data
    networks:
      - amas-backend
      - amas-monitoring
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # ============================================================================
  # DATABASE SERVICES
  # ============================================================================

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: amas-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=amas
      - POSTGRES_USER=amas
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - amas-backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U amas"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: amas-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - amas-backend
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Neo4j (Graph Database - Optional)
  neo4j:
    image: neo4j:5-community
    container_name: amas-neo4j
    restart: unless-stopped
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4J_dbms_memory_pagecache_size=1G
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
    ports:
      - "7474:7474"
      - "7687:7687"
    networks:
      - amas-backend

  # ============================================================================
  # MONITORING STACK (Reference from Part 6B)
  # ============================================================================

  prometheus:
    image: prom/prometheus:latest
    container_name: amas-prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/prometheus/rules:/etc/prometheus/rules
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - amas-monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: amas-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=https://monitoring.your-domain.com
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
      - grafana-data:/var/lib/grafana
    ports:
      - "3001:3000"
    networks:
      - amas-monitoring
    depends_on:
      - prometheus

  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: amas-jaeger
    restart: unless-stopped
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"
      - "4317:4317"
      - "4318:4318"
      - "6831:6831/udp"
    networks:
      - amas-monitoring

  # ============================================================================
  # REVERSE PROXY & SSL
  # ============================================================================

  nginx:
    image: nginx:alpine
    container_name: amas-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/build:/usr/share/nginx/html
    networks:
      - amas-backend
      - amas-monitoring
    depends_on:
      - amas-backend

# ============================================================================
# VOLUMES
# ============================================================================
volumes:
  postgres-data:
  redis-data:
  neo4j-data:
  neo4j-logs:
  prometheus-data:
  grafana-data:
  amas-logs:
  amas-data:

# ============================================================================
# NETWORKS
# ============================================================================
networks:
  amas-backend:
    driver: bridge
  amas-monitoring:
    driver: bridge
```

***

### **Step 8.3: Nginx Configuration**

**File**: `nginx/nginx.conf` (PRODUCTION NGINX)

```nginx
# nginx/nginx.conf (PRODUCTION CONFIGURATION)

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;

    # Upstream backend
    upstream amas_backend {
        least_conn;
        server amas-backend:8000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'" always;

        # Frontend (React App)
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # API Backend
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://amas_backend;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # CORS Headers (if needed)
            add_header Access-Control-Allow-Origin "*" always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
            
            if ($request_method = OPTIONS) {
                return 204;
            }
        }

        # WebSocket
        location /ws {
            proxy_pass http://amas_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_read_timeout 86400;
        }

        # Metrics (restrict access)
        location /metrics {
            allow 10.0.0.0/8;  # Internal network
            deny all;
            
            proxy_pass http://amas_backend;
            proxy_set_header Host $host;
        }

        # Health Check
        location /health {
            access_log off;
            proxy_pass http://amas_backend;
            proxy_set_header Host $host;
        }
    }

    # Grafana
    server {
        listen 443 ssl http2;
        server_name monitoring.your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            proxy_pass http://grafana:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

***

### **Step 8.4: Kubernetes Deployment Configuration**

**File**: `k8s/deployment.yaml` (KUBERNETES MANIFESTS)

```yaml
# k8s/deployment.yaml (KUBERNETES DEPLOYMENT)
apiVersion: v1
kind: Namespace
metadata:
  name: amas-production

---
# ConfigMap for Application Configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: amas-config
  namespace: amas-production
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  JSON_LOGS: "true"
  DATABASE_URL: "postgresql://amas:PASSWORD@postgres-service:5432/amas"
  REDIS_URL: "redis://redis-service:6379/0"
  JAEGER_ENDPOINT: "jaeger-collector:6831"

---
# Secret for Sensitive Data
apiVersion: v1
kind: Secret
metadata:
  name: amas-secrets
  namespace: amas-production
type: Opaque
stringData:
  DB_PASSWORD: "your-secure-db-password"
  SECRET_KEY: "your-secret-key-here"
  JWT_SECRET: "your-jwt-secret-here"
  OPENAI_API_KEY: "your-openai-key"
  ANTHROPIC_API_KEY: "your-anthropic-key"

---
# AMAS Backend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amas-backend
  namespace: amas-production
  labels:
    app: amas-backend
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: amas-backend
  template:
    metadata:
      labels:
        app: amas-backend
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: amas-backend
        image: your-registry/amas-backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        env:
        - name: PORT
          value: "8000"
        envFrom:
        - configMapRef:
            name: amas-config
        - secretRef:
            name: amas-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: data
          mountPath: /app/data
      volumes:
      - name: logs
        emptyDir: {}
      - name: data
        persistentVolumeClaim:
          claimName: amas-data-pvc

---
# Service for Backend
apiVersion: v1
kind: Service
metadata:
  name: amas-backend-service
  namespace: amas-production
  labels:
    app: amas-backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: amas-backend

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: amas-backend-hpa
  namespace: amas-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: amas-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

---
# Ingress for External Access
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: amas-ingress
  namespace: amas-production
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - amas.your-domain.com
    secretName: amas-tls-secret
  rules:
  - host: amas.your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: amas-backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: amas-frontend-service
            port:
              number: 80

---
# PostgreSQL StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: amas-production
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: "amas"
        - name: POSTGRES_USER
          value: "amas"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: amas-secrets
              key: DB_PASSWORD
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi

---
# PostgreSQL Service
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: amas-production
spec:
  clusterIP: None
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: postgres

---
# Redis Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: amas-production
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--appendonly", "yes"]
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc

---
# Redis Service
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: amas-production
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis

---
# PersistentVolumeClaim for Redis
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: amas-production
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
# PersistentVolumeClaim for AMAS Data
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: amas-data-pvc
  namespace: amas-production
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 20Gi
```

***

### **Step 8.5: CI/CD Pipeline - GitHub Actions**

**File**: `.github/workflows/deploy.yml` (COMPLETE CI/CD)

```yaml
# .github/workflows/deploy.yml (GITHUB ACTIONS CI/CD)
name: Build, Test & Deploy

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ============================================================================
  # TESTING
  # ============================================================================
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: amas_test
          POSTGRES_USER: amas
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run database migrations
        env:
          DATABASE_URL: postgresql://amas:test_password@localhost:5432/amas_test
        run: |
          alembic upgrade head
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://amas:test_password@localhost:5432/amas_test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key
          ENVIRONMENT: test
        run: |
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

  # ============================================================================
  # FRONTEND BUILD
  # ============================================================================
  build-frontend:
    name: Build Frontend
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Build frontend
        working-directory: ./frontend
        run: npm run build
      
      - name: Upload frontend build
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/build

  # ============================================================================
  # DOCKER BUILD & PUSH
  # ============================================================================
  build-docker:
    name: Build & Push Docker Image
    runs-on: ubuntu-latest
    needs: [test, build-frontend]
    if: github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Download frontend build
        uses: actions/download-artifact@v3
        with:
          name: frontend-build
          path: frontend/build
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

  # ============================================================================
  # DEPLOY TO PRODUCTION
  # ============================================================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build-docker
    if: github.ref == 'refs/heads/main'
    
    environment:
      name: production
      url: https://amas.your-domain.com
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'
      
      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml
      
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/amas-backend -n amas-production --timeout=5m
      
      - name: Verify deployment
        run: |
          kubectl get pods -n amas-production
          kubectl get services -n amas-production
      
      - name: Run database migrations
        run: |
          kubectl exec -n amas-production deployment/amas-backend -- \
            alembic upgrade head
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment completed! 🚀'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

***

### **Step 8.6: Environment Variables Template**

**File**: `.env.production.example` (PRODUCTION ENV TEMPLATE)

```bash
# .env.production.example (PRODUCTION ENVIRONMENT TEMPLATE)

# ============================================================================
# APPLICATION
# ============================================================================
ENVIRONMENT=production
APP_VERSION=1.0.0
SECRET_KEY=CHANGE_THIS_TO_SECURE_RANDOM_STRING
JWT_SECRET=CHANGE_THIS_TO_SECURE_RANDOM_STRING
CORS_ORIGINS=https://your-domain.com

# ============================================================================
# DATABASE
# ============================================================================
DATABASE_URL=postgresql://amas:SECURE_PASSWORD@postgres:5432/amas
DB_PASSWORD=SECURE_PASSWORD

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=SECURE_REDIS_PASSWORD

# Neo4j (Optional)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=SECURE_NEO4J_PASSWORD

# ============================================================================
# AI PROVIDERS
# ============================================================================
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
DEEPSEEK_API_KEY=...
COHERE_API_KEY=...
TOGETHER_API_KEY=...
# ... add all 16 providers

# ============================================================================
# INTEGRATIONS
# ============================================================================
# GitHub
GITHUB_TOKEN=ghp_...

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

# N8N
N8N_BASE_URL=https://n8n.your-domain.com
N8N_API_KEY=...

# ============================================================================
# MONITORING
# ============================================================================
JAEGER_ENDPOINT=jaeger:6831
OTLP_ENDPOINT=tempo:4317
TRACING_CONSOLE=false

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
JSON_LOGS=true
LOG_FILE=/app/logs/amas.log

# ============================================================================
# GRAFANA
# ============================================================================
GRAFANA_USER=admin
GRAFANA_PASSWORD=SECURE_GRAFANA_PASSWORD

# ============================================================================
# SECURITY
# ============================================================================
RATE_LIMIT_PER_MINUTE=100
MAX_UPLOAD_SIZE_MB=100
SESSION_TIMEOUT_MINUTES=60

# ============================================================================
# PERFORMANCE
# ============================================================================
WORKER_COUNT=4
MAX_CONCURRENT_TASKS=50
TASK_TIMEOUT_SECONDS=300
```

***

**This completes the first major section of Part 8!**

**What's Implemented**:
1. ✅ Production Dockerfile (multi-stage, optimized)
2. ✅ Docker Compose (complete stack)
3. ✅ Nginx configuration (SSL, reverse proxy, security)
4. ✅ Kubernetes manifests (deployment, services, HPA, ingress)
5. ✅ CI/CD pipeline (GitHub Actions)
6. ✅ Environment configuration

**now lets move into:**:
- Database migration system (Alembic)
- Backup & disaster recovery scripts
- Security hardening guide
- Performance tuning guide
- Scaling strategy


# **🎯 AMAS PROJECT: PART 8B - DATABASE MIGRATIONS, BACKUP, SECURITY & SCALING**
## **Complete Production Operations Guide**

---

## **PART 8B: PRODUCTION OPERATIONS & DEPLOYMENT (FINAL)**

### **Step 8B.1: Database Migration System (Alembic)**

**File**: `alembic.ini` (PRODUCTION-READY)

```ini
# alembic.ini (PRODUCTION CONFIGURATION)

[alembic]
# Path to migration scripts
script_location = alembic

# Template used to generate migration file names
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# Timezone for migration timestamps
timezone = UTC

# Prepend sys.path
prepend_sys_path = .

# Version path separator
version_path_separator = os

# Output encoding
output_encoding = utf-8

# Database URL (use environment variable in production)
sqlalchemy.url = driver://user:pass@localhost/dbname

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

***

**File**: `alembic/env.py` (MIGRATION ENVIRONMENT)

```python
# alembic/env.py (PRODUCTION MIGRATION ENVIRONMENT)
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Import all models
from src.database.models import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata
target_metadata = Base.metadata

def get_url():
    """Get database URL from environment"""
    return os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

***

**File**: `alembic/versions/001_initial_schema.py` (INITIAL MIGRATION)

```python
# alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create initial database schema"""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('roles', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('permissions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'])
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'])
    
    # Agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('capabilities', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('configuration', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('expertise_score', sa.Numeric(5, 4), nullable=True, server_default='0.9000'),
        sa.Column('total_executions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('successful_executions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('failed_executions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id')
    )
    op.create_index(op.f('ix_agents_agent_id'), 'agents', ['agent_id'])
    op.create_index(op.f('ix_agents_status'), 'agents', ['status'])
    
    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(100), nullable=False),
        sa.Column('target', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('assigned_agents', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error_details', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id')
    )
    op.create_index(op.f('ix_tasks_task_id'), 'tasks', ['task_id'])
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'])
    op.create_index(op.f('ix_tasks_created_at'), 'tasks', ['created_at'])

def downgrade() -> None:
    """Drop all tables"""
    op.drop_index(op.f('ix_tasks_created_at'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_task_id'), table_name='tasks')
    op.drop_table('tasks')
    
    op.drop_index(op.f('ix_agents_status'), table_name='agents')
    op.drop_index(op.f('ix_agents_agent_id'), table_name='agents')
    op.drop_table('agents')
    
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

***

### **Step 8B.2: Backup & Disaster Recovery**

**File**: `scripts/backup.sh` (AUTOMATED BACKUP SCRIPT)

```bash
#!/bin/bash
# scripts/backup.sh (PRODUCTION BACKUP SCRIPT)

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-s3://your-bucket/amas-backups}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Database credentials
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-amas}"
DB_USER="${DB_USER:-amas}"
DB_PASSWORD="${DB_PASSWORD}"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="amas_backup_${ENVIRONMENT}_${TIMESTAMP}"

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
    exit 1
}

# ============================================================================
# BACKUP POSTGRESQL
# ============================================================================
backup_postgresql() {
    log "Starting PostgreSQL backup..."
    
    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}_postgres.sql.gz"
    
    # Create backup directory
    mkdir -p "${BACKUP_DIR}"
    
    # Dump database
    PGPASSWORD="${DB_PASSWORD}" pg_dump \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --format=custom \
        --compress=9 \
        --verbose \
        | gzip > "${backup_file}"
    
    if [ $? -eq 0 ]; then
        log "PostgreSQL backup completed: ${backup_file}"
        log "Backup size: $(du -h ${backup_file} | cut -f1)"
    else
        error "PostgreSQL backup failed"
    fi
}

# ============================================================================
# BACKUP REDIS
# ============================================================================
backup_redis() {
    log "Starting Redis backup..."
    
    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}_redis.rdb"
    
    # Trigger Redis save
    docker exec amas-redis redis-cli BGSAVE
    
    # Wait for save to complete
    while [ "$(docker exec amas-redis redis-cli LASTSAVE)" = "0" ]; do
        sleep 1
    done
    
    # Copy RDB file
    docker cp amas-redis:/data/dump.rdb "${backup_file}"
    
    if [ $? -eq 0 ]; then
        log "Redis backup completed: ${backup_file}"
    else
        error "Redis backup failed"
    fi
}

# ============================================================================
# BACKUP APPLICATION DATA
# ============================================================================
backup_app_data() {
    log "Starting application data backup..."
    
    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}_appdata.tar.gz"
    
    # Backup logs and data directories
    tar -czf "${backup_file}" \
        -C /app \
        logs/ \
        data/ \
        2>/dev/null || true
    
    if [ $? -eq 0 ]; then
        log "Application data backup completed: ${backup_file}"
    else
        log "Warning: Application data backup incomplete"
    fi
}

# ============================================================================
# UPLOAD TO S3
# ============================================================================
upload_to_s3() {
    log "Uploading backups to S3..."
    
    # Check if AWS CLI is available
    if ! command -v aws &> /dev/null; then
        log "Warning: AWS CLI not found, skipping S3 upload"
        return 0
    fi
    
    # Upload all backup files
    aws s3 sync "${BACKUP_DIR}" "${S3_BUCKET}/${ENVIRONMENT}/" \
        --exclude "*" \
        --include "*${BACKUP_NAME}*" \
        --storage-class STANDARD_IA
    
    if [ $? -eq 0 ]; then
        log "S3 upload completed"
    else
        error "S3 upload failed"
    fi
}

# ============================================================================
# CLEANUP OLD BACKUPS
# ============================================================================
cleanup_old_backups() {
    log "Cleaning up old backups (retention: ${RETENTION_DAYS} days)..."
    
    # Delete local backups older than retention period
    find "${BACKUP_DIR}" -type f -mtime +${RETENTION_DAYS} -delete
    
    # Delete old S3 backups
    if command -v aws &> /dev/null; then
        aws s3 ls "${S3_BUCKET}/${ENVIRONMENT}/" | while read -r line; do
            backup_date=$(echo $line | awk '{print $1}')
            backup_file=$(echo $line | awk '{print $4}')
            
            if [ -n "$backup_date" ]; then
                backup_timestamp=$(date -d "$backup_date" +%s)
                current_timestamp=$(date +%s)
                age_days=$(( (current_timestamp - backup_timestamp) / 86400 ))
                
                if [ $age_days -gt $RETENTION_DAYS ]; then
                    log "Deleting old S3 backup: ${backup_file}"
                    aws s3 rm "${S3_BUCKET}/${ENVIRONMENT}/${backup_file}"
                fi
            fi
        done
    fi
    
    log "Cleanup completed"
}

# ============================================================================
# VERIFY BACKUP
# ============================================================================
verify_backup() {
    log "Verifying backup integrity..."
    
    local postgres_backup="${BACKUP_DIR}/${BACKUP_NAME}_postgres.sql.gz"
    
    # Verify PostgreSQL backup
    if [ -f "${postgres_backup}" ]; then
        gzip -t "${postgres_backup}"
        if [ $? -eq 0 ]; then
            log "PostgreSQL backup verification: OK"
        else
            error "PostgreSQL backup verification failed"
        fi
    fi
    
    log "Backup verification completed"
}

# ============================================================================
# SEND NOTIFICATION
# ============================================================================
send_notification() {
    local status=$1
    local message=$2
    
    # Send to Slack (if webhook configured)
    if [ -n "${SLACK_WEBHOOK}" ]; then
        curl -X POST "${SLACK_WEBHOOK}" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"Backup ${status}: ${message}\"}"
    fi
    
    log "Notification sent: ${status}"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    log "========================================="
    log "AMAS Backup Script"
    log "Environment: ${ENVIRONMENT}"
    log "Backup Name: ${BACKUP_NAME}"
    log "========================================="
    
    # Execute backup steps
    backup_postgresql
    backup_redis
    backup_app_data
    
    # Verify backup
    verify_backup
    
    # Upload to S3
    upload_to_s3
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Calculate total backup size
    total_size=$(du -sh "${BACKUP_DIR}" | cut -f1)
    log "Total backup size: ${total_size}"
    
    # Send success notification
    send_notification "SUCCESS" "Backup completed successfully (${total_size})"
    
    log "========================================="
    log "Backup completed successfully!"
    log "========================================="
}

# Run main function
main

exit 0
```

***

**File**: `scripts/restore.sh` (DATABASE RESTORATION SCRIPT)

```bash
#!/bin/bash
# scripts/restore.sh (PRODUCTION RESTORE SCRIPT)

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================
BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-amas}"
DB_USER="${DB_USER:-amas}"
DB_PASSWORD="${DB_PASSWORD}"

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
    exit 1
}

# ============================================================================
# LIST AVAILABLE BACKUPS
# ============================================================================
list_backups() {
    log "Available backups:"
    ls -lh "${BACKUP_DIR}"/*_postgres.sql.gz | awk '{print $9, $5}'
}

# ============================================================================
# RESTORE POSTGRESQL
# ============================================================================
restore_postgresql() {
    local backup_file=$1
    
    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
    fi
    
    log "========================================="
    log "WARNING: This will REPLACE the current database!"
    log "Backup file: ${backup_file}"
    log "========================================="
    read -p "Continue? (yes/no): " confirm
    
    if [ "${confirm}" != "yes" ]; then
        log "Restore cancelled"
        exit 0
    fi
    
    log "Dropping existing database..."
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d postgres \
        -c "DROP DATABASE IF EXISTS ${DB_NAME};"
    
    log "Creating new database..."
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d postgres \
        -c "CREATE DATABASE ${DB_NAME};"
    
    log "Restoring database from backup..."
    gunzip -c "${backup_file}" | PGPASSWORD="${DB_PASSWORD}" pg_restore \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --verbose
    
    if [ $? -eq 0 ]; then
        log "Database restored successfully!"
    else
        error "Database restore failed"
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    if [ -z "$1" ]; then
        list_backups
        echo ""
        echo "Usage: $0 <backup_file>"
        exit 1
    fi
    
    restore_postgresql "$1"
}

main "$@"
```

***

### **Step 8B.3: Security Hardening Guide**

**File**: `docs/SECURITY.md` (PRODUCTION SECURITY GUIDE)

```markdown
# AMAS Security Hardening Guide

## 1. Authentication & Authorization

### 1.1 JWT Token Security
```
# Implement token rotation
JWT_EXPIRATION = 15 * 60  # 15 minutes
REFRESH_TOKEN_EXPIRATION = 7 * 24 * 60 * 60  # 7 days

# Use strong secret keys (minimum 32 bytes)
SECRET_KEY = secrets.token_urlsafe(32)
JWT_SECRET = secrets.token_urlsafe(32)
```

### 1.2 Password Policy
- Minimum 12 characters
- Require uppercase, lowercase, numbers, special characters
- Use bcrypt with cost factor 12+
- Implement password history (prevent reuse)
- Enable account lockout after 5 failed attempts

### 1.3 Multi-Factor Authentication (MFA)
```
# Enable MFA for all admin accounts
MFA_REQUIRED_ROLES = ['admin', 'security_admin']
MFA_METHODS = ['totp', 'sms', 'email']
```

## 2. API Security

### 2.1 Rate Limiting
```
# Nginx configuration
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
```

### 2.2 Input Validation
- Validate all user inputs
- Use Pydantic models for request validation
- Sanitize HTML/SQL to prevent injection
- Implement file upload restrictions (size, type)

### 2.3 CORS Configuration
```
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE"]
```

## 3. Database Security

### 3.1 Connection Security
```
# Use SSL/TLS for database connections
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# Rotate database passwords quarterly
# Use separate credentials for different environments
```

### 3.2 SQL Injection Prevention
- Use parameterized queries (ALWAYS)
- Never concatenate user input into SQL
- Use ORM (SQLAlchemy) for complex queries

### 3.3 Data Encryption
```
# Encrypt sensitive fields at rest
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

## 4. Network Security

### 4.1 HTTPS/TLS
- Use TLS 1.2 or higher
- Strong cipher suites only
- Implement HSTS (HTTP Strict Transport Security)
- Renew certificates before expiration

### 4.2 Firewall Rules
```
# Allow only necessary ports
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP (redirect to HTTPS)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH (from specific IPs only)
iptables -A INPUT -j DROP  # Drop all other traffic
```

### 4.3 DDoS Protection
- Use Cloudflare or AWS WAF
- Implement request throttling
- Set up IP whitelisting for admin endpoints

## 5. Secrets Management

### 5.1 Environment Variables
```
# Never commit secrets to Git
# Use secret management services
export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id prod/db/url --query SecretString --output text)
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id prod/openai/key --query SecretString --output text)
```

### 5.2 Kubernetes Secrets
```
apiVersion: v1
kind: Secret
metadata:
  name: amas-secrets
type: Opaque
data:
  db-password: <base64-encoded>
  jwt-secret: <base64-encoded>
```

### 5.3 Secret Rotation
- Rotate all secrets every 90 days
- Implement automated rotation for API keys
- Log all secret access

## 6. Logging & Monitoring

### 6.1 Security Logging
```
# Log all security events
security_logger.info(
    "login_attempt",
    extra={
        "user_id": user_id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "success": True
    }
)
```

### 6.2 Audit Trail
- Log all administrative actions
- Track data access and modifications
- Retain logs for minimum 1 year
- Enable log encryption

### 6.3 Security Alerts
```
# Prometheus alert rules
- alert: MultipleFailedLogins
  expr: rate(login_failures[5m]) > 10
  annotations:
    summary: "Multiple failed login attempts detected"
    
- alert: UnauthorizedAccess
  expr: rate(http_requests_total{status="403"}[5m]) > 5
  annotations:
    summary: "High rate of unauthorized access attempts"
```

## 7. Container Security

### 7.1 Docker Best Practices
```
# Use minimal base images
FROM python:3.11-slim

# Run as non-root user
USER amas

# Scan images for vulnerabilities
# trivy image your-image:latest
```

### 7.2 Kubernetes Security
```
# Security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true
```

## 8. Dependency Management

### 8.1 Vulnerability Scanning
```
# Scan Python dependencies
pip-audit

# Scan npm dependencies
npm audit

# Automated scanning in CI/CD
- name: Security scan
  run: |
    pip install safety
    safety check --json
```

### 8.2 Update Policy
- Review and update dependencies monthly
- Subscribe to security advisories
- Test updates in staging before production

## 9. Incident Response

### 9.1 Response Plan
1. **Detection** - Automated alerts via Prometheus/Grafana
2. **Assessment** - Evaluate severity and impact
3. **Containment** - Isolate affected systems
4. **Eradication** - Remove threat
5. **Recovery** - Restore from backup if needed
6. **Post-Incident** - Document and improve

### 9.2 Emergency Contacts
```
oncall:
  - role: Security Lead
    contact: security@your-domain.com
    phone: +1-xxx-xxx-xxxx
  - role: DevOps Lead
    contact: devops@your-domain.com
    phone: +1-xxx-xxx-xxxx
```

## 10. Compliance

### 10.1 GDPR Compliance
- Implement right to access
- Implement right to be forgotten
- Data minimization
- Consent management

### 10.2 SOC 2 Compliance
- Access controls
- Encryption at rest and in transit
- Audit logging
- Incident response procedures

## Security Checklist

- [ ] All secrets in secret manager (not in code)
- [ ] HTTPS/TLS enabled with strong ciphers
- [ ] Rate limiting configured
- [ ] Authentication with MFA for admins
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] CORS properly configured
- [ ] Security headers set (HSTS, CSP, X-Frame-Options)
- [ ] Container images scanned for vulnerabilities
- [ ] Logging and monitoring active
- [ ] Automated backups configured
- [ ] Disaster recovery plan documented
- [ ] Security incident response plan
- [ ] Regular security audits scheduled
```

***

### **Step 8B.4: Performance Tuning Guide**

**File**: `docs/PERFORMANCE.md` (PERFORMANCE OPTIMIZATION)

```markdown
# AMAS Performance Tuning Guide

## 1. Database Optimization

### 1.1 Connection Pooling
```
# Optimal pool settings
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
```

### 1.2 Index Strategy
```
-- Create indexes for frequently queried columns
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Composite indexes for complex queries
CREATE INDEX idx_tasks_user_status ON tasks(created_by, status) 
WHERE status IN ('executing', 'pending');

-- Partial indexes for specific conditions
CREATE INDEX idx_active_tasks ON tasks(task_id) 
WHERE status = 'executing';
```

### 1.3 Query Optimization
```
# Use pagination
tasks = await db.fetch(
    "SELECT * FROM tasks ORDER BY created_at DESC LIMIT $1 OFFSET $2",
    limit, offset
)

# Avoid N+1 queries - use joins
tasks_with_agents = await db.fetch("""
    SELECT t.*, a.name as agent_name
    FROM tasks t
    LEFT JOIN agents a ON a.agent_id = ANY(t.assigned_agents)
    WHERE t.status = 'executing'
""")

# Use EXPLAIN ANALYZE to identify slow queries
EXPLAIN ANALYZE SELECT * FROM tasks WHERE status = 'executing';
```

### 1.4 PostgreSQL Tuning
```
# postgresql.conf optimizations
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 20MB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

## 2. Redis Optimization

### 2.1 Cache Strategy
```
# Cache frequently accessed data
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# Cache patterns
async def get_task_with_cache(task_id: str):
    cache_key = f"task:{task_id}"
    
    # Try cache first
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    task = await db.fetchrow("SELECT * FROM tasks WHERE task_id = $1", task_id)
    
    # Cache result
    await redis.set(cache_key, json.dumps(dict(task)), ex=CACHE_TTL_MEDIUM)
    
    return task
```

### 2.2 Cache Invalidation
```
# Invalidate on update
async def update_task(task_id: str, data: dict):
    await db.execute("UPDATE tasks SET ... WHERE task_id = $1", task_id)
    await redis.delete(f"task:{task_id}")
```

## 3. API Performance

### 3.1 Async Everything
```
# Use async/await for all I/O operations
@app.get("/tasks")
async def list_tasks(db = Depends(get_db)):
    tasks = await db.fetch("SELECT * FROM tasks")
    return tasks

# Concurrent execution
results = await asyncio.gather(
    db.fetch("SELECT * FROM tasks"),
    db.fetch("SELECT * FROM agents"),
    redis.get("stats")
)
```

### 3.2 Response Compression
```
# Enable gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 3.3 Pagination
```
# Always paginate large responses
@app.get("/tasks")
async def list_tasks(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    tasks = await db.fetch(
        "SELECT * FROM tasks LIMIT $1 OFFSET $2",
        limit, offset
    )
    total = await db.fetchval("SELECT COUNT(*) FROM tasks")
    
    return {
        "items": tasks,
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

## 4. AI Provider Optimization

### 4.1 Response Caching
```
# Cache AI responses for identical prompts
async def generate_with_cache(prompt: str):
    cache_key = f"ai:response:{hashlib.md5(prompt.encode()).hexdigest()}"
    
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    response = await ai_provider.generate(prompt)
    
    # Cache for 1 hour
    await redis.set(cache_key, json.dumps(response), ex=3600)
    
    return response
```

### 4.2 Batch Processing
```
# Process multiple tasks in parallel
async def process_tasks_batch(tasks: List[Task]):
    async with asyncio.TaskGroup() as tg:
        for task in tasks:
            tg.create_task(execute_task(task))
```

## 5. Frontend Optimization

### 5.1 Code Splitting
```
// Lazy load components
const Dashboard = React.lazy(() => import('./components/Dashboard'));
const TaskList = React.lazy(() => import('./components/TaskList'));
```

### 5.2 Asset Optimization
```
// package.json build optimization
{
  "scripts": {
    "build": "react-scripts build && npm run optimize",
    "optimize": "npx imagemin build/static/**/*.{jpg,png} --out-dir=build/static"
  }
}
```

## 6. Monitoring & Profiling

### 6.1 Application Profiling
```
# Profile slow endpoints
import cProfile
import pstats

def profile_endpoint():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Execute code
    result = expensive_operation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

### 6.2 Query Performance Monitoring
```
# Log slow queries
async def execute_with_monitoring(query: str, *args):
    start = time.time()
    result = await db.fetch(query, *args)
    duration = time.time() - start
    
    if duration > 1.0:  # Slow query threshold
        logger.warning(f"Slow query ({duration:.2f}s): {query}")
    
    return result
```

## Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time (p95) | < 200ms | < 500ms |
| Database Query Time (p95) | < 50ms | < 200ms |
| Task Execution Time | < 30s | < 60s |
| Frontend Load Time | < 2s | < 4s |
| WebSocket Latency | < 100ms | < 300ms |
| Cache Hit Rate | > 80% | > 60% |
| Error Rate | < 0.1% | < 1% |
```

***

### **Step 8B.5: Scaling Strategy**

**File**: `docs/SCALING.md` (SCALING GUIDE)

```markdown
# AMAS Scaling Strategy

## 1. Horizontal Scaling

### 1.1 Application Layer
```
# Kubernetes HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: amas-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: amas-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### 1.2 Database Scaling
```
# PostgreSQL read replicas
replication:
  enabled: true
  readReplicas: 3
  syncMode: async

# Connection pooling
pgbouncer:
  enabled: true
  poolMode: transaction
  maxClientConn: 1000
  defaultPoolSize: 25
```

### 1.3 Redis Clustering
```
# Redis Cluster configuration
redis:
  cluster:
    enabled: true
    nodes: 6
    replicas: 1
  persistence:
    enabled: true
    rdb:
      enabled: true
      save: "900 1 300 10 60 10000"
    aof:
      enabled: true
```

## 2. Vertical Scaling

### 2.1 Resource Allocation
```
# Production resource limits
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"
```

### 2.2 Database Sizing
```
-- Recommended PostgreSQL instance sizes
Development: 2 vCPU, 4GB RAM, 50GB SSD
Staging: 4 vCPU, 8GB RAM, 100GB SSD
Production: 8 vCPU, 32GB RAM, 500GB SSD (minimum)
Production (High Load): 16 vCPU, 64GB RAM, 1TB SSD
```

## 3. Load Balancing

### 3.1 Application Load Balancer
```
# AWS ALB configuration
LoadBalancer:
  Type: application
  Scheme: internet-facing
  HealthCheck:
    Path: /health
    Interval: 30
    Timeout: 5
    HealthyThreshold: 2
    UnhealthyThreshold: 3
  Stickiness:
    Enabled: true
    Duration: 3600
```

### 3.2 Geographic Distribution
```
# Multi-region deployment
regions:
  - us-east-1  # Primary
  - eu-west-1  # Secondary
  - ap-southeast-1  # Tertiary

# DNS routing
route53:
  routingPolicy: latency-based
  healthCheck: enabled
```

## 4. Caching Strategy

### 4.1 Multi-Layer Caching
```
Browser Cache (1 hour)
  ↓
CDN Cache (24 hours)
  ↓
Redis Cache (5 minutes)
  ↓
Database
```

### 4.2 Cache Warming
```
# Pre-warm cache on deployment
async def warm_cache():
    # Cache frequently accessed data
    tasks = await db.fetch("SELECT * FROM tasks WHERE status = 'executing'")
    for task in tasks:
        await redis.set(f"task:{task['task_id']}", json.dumps(dict(task)))
    
    agents = await db.fetch("SELECT * FROM agents WHERE status = 'active'")
    for agent in agents:
        await redis.set(f"agent:{agent['agent_id']}", json.dumps(dict(agent)))
```

## 5. Queue Management

### 5.1 Task Queue Scaling
```
# Celery worker autoscaling
CELERYD_AUTOSCALER = "10,50"  # Min 10, max 50 workers
CELERYD_PREFETCH_MULTIPLIER = 4
CELERY_ACKS_LATE = True
```

### 5.2 Priority Queues
```
# Different queues for different priorities
CELERY_ROUTES = {
    'tasks.critical': {'queue': 'critical'},
    'tasks.high': {'queue': 'high'},
    'tasks.normal': {'queue': 'normal'},
    'tasks.low': {'queue': 'low'},
}
```

## 6. Monitoring at Scale

### 6.1 Metrics Aggregation
```
# Prometheus federation for multi-cluster
scrape_configs:
  - job_name: 'federate'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{__name__=~"amas_.*"}'
    static_configs:
      - targets:
        - 'prometheus-us-east-1:9090'
        - 'prometheus-eu-west-1:9090'
```

## Scaling Thresholds

| Metric | Scale Up | Scale Down |
|--------|----------|------------|
| CPU Usage | > 70% for 5 min | < 30% for 10 min |
| Memory Usage | > 80% for 5 min | < 40% for 10 min |
| Request Queue | > 100 pending | < 10 pending |
| Response Time (p95) | > 500ms | < 100ms |
| Error Rate | > 1% | < 0.1% |
```

***

**This completes Part 8B - Production Deployment & Operations!** 🎉

**What's Fully Implemented in Part 8**:
1. ✅ Production Dockerfile (multi-stage, optimized)
2. ✅ Docker Compose (complete stack)
3. ✅ Nginx configuration (SSL, security headers, rate limiting)
4. ✅ Kubernetes manifests (deployment, HPA, ingress, StatefulSets)
5. ✅ CI/CD pipeline (GitHub Actions - test, build, deploy)
6. ✅ Database migrations (Alembic)
7. ✅ Backup & restore scripts (automated, S3 upload)
8. ✅ Security hardening guide (authentication, encryption, compliance)
9. ✅ Performance tuning guide (database, caching, API optimization)
10. ✅ Scaling strategy (horizontal/vertical, load balancing, multi-region)

**Next Steps**:
- **Part 9**: Testing Strategy & Implementation
- **Part 10**: Final Production Checklist & Documentation
