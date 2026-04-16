# 🚀 دليل تشغيل AMAS في وضع الإنتاج (Production Mode)

## 📋 المتطلبات الأساسية

### 1. المتطلبات البرمجية
- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose** (موصى به)
- **PostgreSQL 15+** (أو Docker)
- **Redis 7+** (أو Docker)
- **Neo4j 5+** (أو Docker)

### 2. إعداد ملف `.env` للإنتاج

أنشئ ملف `.env` في المجلد الرئيسي للمشروع:

```env
# ============================================
# AMAS PRODUCTION CONFIGURATION
# ============================================

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=your_secure_secret_key_change_this_in_production
JWT_SECRET_KEY=your_jwt_secret_key_change_this_in_production

# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=postgresql://postgres:your_secure_password_here@localhost:5432/amas
POSTGRES_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=amas
DB_USER=postgres
DB_PASSWORD=your_secure_password_here

# ============================================
# REDIS CONFIGURATION
# ============================================
REDIS_URL=redis://:your_redis_password_here@localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0

# ============================================
# NEO4J CONFIGURATION
# ============================================
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# ============================================
# OLLAMA CONFIGURATION (Local AI Models)
# ============================================
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=deepseek-r1:8b

# ============================================
# AI PROVIDERS (Optional - for cloud AI)
# ============================================
# Tier 1 - Premium Speed & Quality
CEREBRAS_API_KEY=your_cerebras_key
NVIDIA_API_KEY=your_nvidia_key
GROQ2_API_KEY=your_groq2_key
GROQAI_API_KEY=your_groqai_key

# Tier 2 - High Quality
DEEPSEEK_API_KEY=your_deepseek_key
CODESTRAL_API_KEY=your_codestral_key
GLM_API_KEY=your_glm_key
GEMINI2_API_KEY=your_gemini2_key
GROK_API_KEY=your_grok_key

# Tier 3 - Enterprise
COHERE_API_KEY=your_cohere_key

# Tier 4 - Reliable Fallbacks
KIMI_API_KEY=your_kimi_key
QWEN_API_KEY=your_qwen_key
GPTOSS_API_KEY=your_gptoss_key
CHUTES_API_KEY=your_chutes_key

# ============================================
# EMAIL SERVICE (Optional)
# ============================================
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@amas.com
SMTP_FROM_NAME=AMAS System

# ============================================
# FRONTEND CONFIGURATION
# ============================================
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🐳 الطريقة 1: استخدام Docker Compose (موصى به)

### الخطوة 1: إعداد ملف `.env`

```powershell
# نسخ ملف المثال
Copy-Item .env.example .env

# تعديل ملف .env باستخدام محرر النصوص
notepad .env
```

### الخطوة 2: تشغيل جميع الخدمات

```powershell
# الانتقال إلى مجلد المشروع
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System

# تشغيل جميع الخدمات (PostgreSQL, Redis, Neo4j, Backend, Frontend)
docker-compose up -d --build

# عرض حالة الخدمات
docker-compose ps

# عرض Logs
docker-compose logs -f
```

### الخطوة 3: التحقق من حالة الخدمات

```powershell
# التحقق من صحة النظام
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# عرض Logs لخدمة معينة
docker-compose logs -f amas
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f neo4j
```

### الوصول إلى الخدمات

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Neo4j Browser**: http://localhost:7474
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

---

## 🔧 الطريقة 2: التشغيل اليدوي (Manual)

### الخطوة 1: تشغيل PostgreSQL

#### باستخدام Docker:
```powershell
docker run -d `
  --name amas-postgres `
  -e POSTGRES_DB=amas `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=your_secure_password_here `
  -p 5432:5432 `
  -v postgres_data:/var/lib/postgresql/data `
  postgres:15-alpine
```

#### أو باستخدام PostgreSQL المثبت محلياً:
```powershell
# إنشاء قاعدة البيانات
psql -U postgres -c "CREATE DATABASE amas;"

# إنشاء المستخدم (إذا لزم الأمر)
psql -U postgres -c "CREATE USER postgres WITH PASSWORD 'your_secure_password_here';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE amas TO postgres;"
```

### الخطوة 2: تشغيل Redis

#### باستخدام Docker:
```powershell
docker run -d `
  --name amas-redis `
  -p 6379:6379 `
  -v redis_data:/data `
  redis:7-alpine redis-server --appendonly yes --requirepass your_redis_password_here
```

#### أو باستخدام Redis المثبت محلياً:
```powershell
# تشغيل Redis service
redis-server --requirepass your_redis_password_here
```

### الخطوة 3: تشغيل Neo4j

#### باستخدام Docker:
```powershell
docker run -d `
  --name amas-neo4j `
  -p 7474:7474 `
  -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/your_neo4j_password_here `
  -e NEO4J_PLUGINS=["apoc","graph-data-science"] `
  -v neo4j_data:/data `
  -v neo4j_logs:/logs `
  neo4j:5
```

### الخطوة 4: تشغيل Alembic Migrations

```powershell
# الانتقال إلى مجلد المشروع
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System

# تشغيل Migrations
alembic upgrade head
```

### الخطوة 5: تشغيل Backend (Production Mode)

```powershell
# تعيين متغيرات البيئة
$env:ENVIRONMENT="production"
$env:DATABASE_URL="postgresql://postgres:your_secure_password_here@localhost:5432/amas"
$env:REDIS_URL="redis://:your_redis_password_here@localhost:6379/0"
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="your_neo4j_password_here"

# تشغيل Backend (بدون reload في production)
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**ملاحظة**: في production، استخدم `--workers` بدلاً من `--reload` لتحسين الأداء.

### الخطوة 6: تشغيل Frontend (Production Mode)

#### في نافذة PowerShell منفصلة:

```powershell
# الانتقال إلى مجلد Frontend
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System\frontend

# بناء Frontend للإنتاج
npm run build

# تشغيل Frontend (Production build)
npm run preview
```

**أو استخدام serve:**

```powershell
# تثبيت serve
npm install -g serve

# تشغيل Frontend build
serve -s dist -l 3000
```

---

## 🚀 سكريبت تشغيل تلقائي (Windows PowerShell)

أنشئ ملف `start-production.ps1`:

```powershell
# start-production.ps1
# AMAS Production Startup Script

Write-Host "🚀 Starting AMAS in Production Mode..." -ForegroundColor Cyan

# التحقق من Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker found" -ForegroundColor Green
    
    # تشغيل PostgreSQL
    Write-Host "📦 Starting PostgreSQL..." -ForegroundColor Yellow
    docker start amas-postgres 2>$null
    if ($LASTEXITCODE -ne 0) {
        docker run -d --name amas-postgres `
            -e POSTGRES_DB=amas `
            -e POSTGRES_USER=postgres `
            -e POSTGRES_PASSWORD=amas_password `
            -p 5432:5432 `
            -v postgres_data:/var/lib/postgresql/data `
            postgres:15-alpine
    }
    
    # تشغيل Redis
    Write-Host "📦 Starting Redis..." -ForegroundColor Yellow
    docker start amas-redis 2>$null
    if ($LASTEXITCODE -ne 0) {
        docker run -d --name amas-redis `
            -p 6379:6379 `
            -v redis_data:/data `
            redis:7-alpine redis-server --appendonly yes --requirepass amas_redis_password
    }
    
    # تشغيل Neo4j
    Write-Host "📦 Starting Neo4j..." -ForegroundColor Yellow
    docker start amas-neo4j 2>$null
    if ($LASTEXITCODE -ne 0) {
        docker run -d --name amas-neo4j `
            -p 7474:7474 `
            -p 7687:7687 `
            -e NEO4J_AUTH=neo4j/amas_password `
            -v neo4j_data:/data `
            -v neo4j_logs:/logs `
            neo4j:5
    }
    
    Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# تعيين متغيرات البيئة
$env:ENVIRONMENT="production"
$env:DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
$env:REDIS_URL="redis://:amas_redis_password@localhost:6379/0"
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="amas_password"

# تشغيل Migrations
Write-Host "🔄 Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

# تشغيل Backend
Write-Host "🚀 Starting Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:ENVIRONMENT='production'; `$env:DATABASE_URL='postgresql://postgres:amas_password@localhost:5432/amas'; `$env:REDIS_URL='redis://:amas_redis_password@localhost:6379/0'; `$env:NEO4J_URI='bolt://localhost:7687'; `$env:NEO4J_USER='neo4j'; `$env:NEO4J_PASSWORD='amas_password'; python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --workers 4"

# تشغيل Frontend
Write-Host "🚀 Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run build; npm run preview"

Write-Host "`n✅ AMAS is starting in Production Mode!" -ForegroundColor Green
Write-Host "`n🌐 Access Points:" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Neo4j: http://localhost:7474" -ForegroundColor White
```

**استخدام السكريبت:**

```powershell
.\start-production.ps1
```

---

## ✅ التحقق من حالة الخدمات

### 1. التحقق من Backend

```powershell
# Health Check
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# System Health
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing
```

### 2. التحقق من Database

```powershell
# PostgreSQL
docker exec -it amas-postgres psql -U postgres -d amas -c "SELECT version();"

# أو باستخدام psql محلي
psql -U postgres -d amas -c "SELECT version();"
```

### 3. التحقق من Redis

```powershell
# Redis
docker exec -it amas-redis redis-cli -a amas_redis_password ping

# أو باستخدام redis-cli محلي
redis-cli -a amas_redis_password ping
```

### 4. التحقق من Neo4j

```powershell
# Neo4j
docker exec -it amas-neo4j cypher-shell -u neo4j -p amas_password "RETURN 1;"
```

### 5. التحقق من Frontend

```powershell
# Frontend
Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
```

---

## 🛑 إيقاف الخدمات

### باستخدام Docker Compose:

```powershell
# إيقاف جميع الخدمات
docker-compose down

# إيقاف مع حذف Volumes
docker-compose down -v
```

### يدوياً:

```powershell
# إيقاف Containers
docker stop amas-postgres amas-redis amas-neo4j

# حذف Containers
docker rm amas-postgres amas-redis amas-neo4j
```

---

## 🔍 استكشاف الأخطاء

### مشكلة: Backend لا يعمل

1. **تحقق من Database:**
   ```powershell
   docker exec -it amas-postgres psql -U postgres -d amas -c "\dt"
   ```

2. **تحقق من Redis:**
   ```powershell
   docker exec -it amas-redis redis-cli -a amas_redis_password ping
   ```

3. **تحقق من Logs:**
   ```powershell
   docker-compose logs -f amas
   ```

### مشكلة: Database Migration فشل

```powershell
# إعادة تشغيل Migrations
alembic downgrade base
alembic upgrade head

# أو إعادة إنشاء Database
docker exec -it amas-postgres psql -U postgres -c "DROP DATABASE amas;"
docker exec -it amas-postgres psql -U postgres -c "CREATE DATABASE amas;"
alembic upgrade head
```

### مشكلة: Frontend لا يتصل بـ Backend

1. **تحقق من `VITE_API_URL` في `.env`:**
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   ```

2. **أعد بناء Frontend:**
   ```powershell
   cd frontend
   npm run build
   npm run preview
   ```

---

## 📊 Monitoring في Production

### 1. Prometheus Metrics

- **URL**: http://localhost:9090
- **Metrics Endpoint**: http://localhost:8000/metrics

### 2. Grafana Dashboards

- **URL**: http://localhost:3001
- **Username**: admin
- **Password**: amas_grafana_password

### 3. Health Checks

```powershell
# System Health
curl http://localhost:8000/health

# Detailed Health
curl http://localhost:8000/api/v1/health
```

---

## 🔐 Security Checklist للإنتاج

- [ ] تغيير جميع كلمات المرور الافتراضية
- [ ] تعيين `SECRET_KEY` و `JWT_SECRET_KEY` قويين
- [ ] تعطيل `ENVIRONMENT=production`
- [ ] تفعيل HTTPS (استخدام Nginx مع SSL)
- [ ] تعيين `LOG_LEVEL=INFO` أو `WARNING`
- [ ] إزالة `--reload` من uvicorn
- [ ] استخدام `--workers` لتحسين الأداء
- [ ] تفعيل Rate Limiting
- [ ] تفعيل CORS بشكل صحيح
- [ ] تأمين Database و Redis و Neo4j

---

## 📝 ملاحظات مهمة

1. **في Production:**
   - لا تستخدم `--reload` في uvicorn
   - استخدم `--workers 4` أو أكثر
   - فعّل HTTPS
   - استخدم كلمات مرور قوية
   - راجع Logs بانتظام

2. **Performance:**
   - استخدم Connection Pooling للـ Database
   - استخدم Redis للـ Caching
   - راقب Resource Usage

3. **Backup:**
   - نسخ احتياطي منتظم للـ Database
   - نسخ احتياطي لـ Redis Data
   - نسخ احتياطي لـ Neo4j Data

---

**تم إنشاء هذا الدليل بتاريخ: 2025-12-27**

