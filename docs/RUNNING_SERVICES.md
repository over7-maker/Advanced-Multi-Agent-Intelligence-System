# 🚀 دليل تشغيل AMAS - Backend & Frontend

## 📋 المتطلبات الأساسية

### 1. متغيرات البيئة (Environment Variables)

قبل التشغيل، تأكد من وجود ملف `.env` في المجلد الرئيسي للمشروع مع المتغيرات التالية:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:amas_password@localhost:5432/amas
POSTGRES_PASSWORD=amas_password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development

# Neo4j (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Email Service (Optional)
EMAIL_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=noreply@amas.com
SMTP_FROM_NAME=AMAS System
```

### 2. الخدمات المطلوبة

- **PostgreSQL**: يجب أن يكون قيد التشغيل على المنفذ 5432
- **Redis**: يجب أن يكون قيد التشغيل على المنفذ 6379
- **Neo4j** (اختياري): على المنفذ 7687

---

## 🔧 طريقة 1: التشغيل اليدوي (Manual)

### تشغيل Backend (FastAPI)

#### في PowerShell:

```powershell
# الانتقال إلى مجلد المشروع
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System

# تعيين متغيرات البيئة
$env:ENVIRONMENT="development"
$env:DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
$env:REDIS_URL="redis://localhost:6379/0"

# تشغيل Backend
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### في Command Prompt (CMD):

```cmd
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System
set ENVIRONMENT=development
set DATABASE_URL=postgresql://postgres:amas_password@localhost:5432/amas
set REDIS_URL=redis://localhost:6379/0
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### في Linux/Mac:

```bash
cd /path/to/Advanced-Multi-Agent-Intelligence-System
export ENVIRONMENT=development
export DATABASE_URL=postgresql://postgres:amas_password@localhost:5432/amas
export REDIS_URL=redis://localhost:6379/0
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**النتيجة المتوقعة:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**الوصول إلى Backend:**
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

### تشغيل Frontend (Vite + React)

#### في PowerShell:

```powershell
# الانتقال إلى مجلد Frontend
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System\frontend

# تثبيت Dependencies (إذا لم تكن مثبتة)
npm install

# تشغيل Frontend
npm run dev
```

#### في Command Prompt (CMD):

```cmd
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System\frontend
npm install
npm run dev
```

#### في Linux/Mac:

```bash
cd /path/to/Advanced-Multi-Agent-Intelligence-System/frontend
npm install
npm run dev
```

**النتيجة المتوقعة:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**الوصول إلى Frontend:**
- Main App: http://localhost:5173
- Landing Page: http://localhost:5173/landing
- Testing Dashboard: http://localhost:5173/testing
- Dashboard: http://localhost:5173/dashboard

---

## 🔧 طريقة 2: التشغيل في نوافذ منفصلة (Windows PowerShell)

### تشغيل Backend في نافذة منفصلة:

```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:ENVIRONMENT='development'; `$env:DATABASE_URL='postgresql://postgres:amas_password@localhost:5432/amas'; `$env:REDIS_URL='redis://localhost:6379/0'; cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System; Write-Host '🚀 Starting AMAS Backend...' -ForegroundColor Cyan; python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload"
```

### تشغيل Frontend في نافذة منفصلة:

```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System\frontend; Write-Host '🚀 Starting AMAS Frontend...' -ForegroundColor Cyan; npm run dev"
```

---

## 🔧 طريقة 3: استخدام Docker Compose

### تشغيل جميع الخدمات (Backend + Frontend + Database + Redis):

```bash
docker-compose up -d
```

### إيقاف جميع الخدمات:

```bash
docker-compose down
```

### عرض Logs:

```bash
docker-compose logs -f
```

---

## ✅ التحقق من حالة الخدمات

### التحقق من Backend:

```powershell
# في PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
```

```bash
# في Linux/Mac
curl http://localhost:8000/health
```

**النتيجة المتوقعة:**
```json
{
  "status": "healthy",
  "services": {},
  "timestamp": "2025-12-27T..."
}
```

### التحقق من Frontend:

```powershell
# في PowerShell
Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing
```

```bash
# في Linux/Mac
curl http://localhost:5173
```

---

## 🛑 إيقاف الخدمات

### إيقاف Backend:
- اضغط `Ctrl + C` في نافذة Backend

### إيقاف Frontend:
- اضغط `Ctrl + C` في نافذة Frontend

### إيقاف جميع العمليات (PowerShell):

```powershell
Get-Process | Where-Object { $_.ProcessName -eq "python" -or $_.ProcessName -eq "node" } | Stop-Process -Force
```

---

## 🔍 استكشاف الأخطاء

### مشكلة: Backend لا يعمل

1. **تحقق من قاعدة البيانات:**
   ```powershell
   # تحقق من اتصال PostgreSQL
   psql -U postgres -d amas -h localhost
   ```

2. **تحقق من Redis:**
   ```powershell
   # تحقق من اتصال Redis
   redis-cli ping
   ```

3. **تحقق من المتغيرات البيئية:**
   ```powershell
   $env:DATABASE_URL
   $env:REDIS_URL
   $env:ENVIRONMENT
   ```

4. **تحقق من المنافذ:**
   ```powershell
   # تحقق من المنفذ 8000
   netstat -ano | findstr :8000
   ```

### مشكلة: Frontend لا يعمل

1. **تأكد من تثبيت Dependencies:**
   ```powershell
   cd frontend
   npm install
   ```

2. **تحقق من ملف `.env` في Frontend:**
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **امسح Cache وأعد التثبيت:**
   ```powershell
   cd frontend
   Remove-Item -Recurse -Force node_modules
   Remove-Item package-lock.json
   npm install
   ```

4. **تحقق من المنافذ:**
   ```powershell
   # تحقق من المنفذ 5173
   netstat -ano | findstr :5173
   ```

---

## 🚀 تشغيل في وضع الإنتاج (Production Mode)

للحصول على دليل شامل لتشغيل Frontend والBackend في وضع الإنتاج، راجع:

📖 **[دليل تشغيل الإنتاج الكامل](PRODUCTION_STARTUP_GUIDE_AR.md)**

### الطريقة السريعة:

```cmd
REM 1. إعادة بناء Frontend
scripts\rebuild_frontend_production.bat

REM 2. تشغيل جميع الخدمات
scripts\start_production_services.bat
```

### الفرق بين Development و Production:

| الميزة | Development | Production |
|--------|------------|------------|
| **Frontend Port** | 5173 | 4173 |
| **الأمر** | `npm run dev` | `npm run preview` |
| **Hot Reload** | ✅ نعم | ❌ لا |
| **Build Required** | ❌ لا | ✅ نعم |

---

## 📝 ملاحظات مهمة

1. **Backend يجب أن يعمل قبل Frontend** لأن Frontend يحتاج إلى الاتصال بـ Backend API.

2. **في وضع Development** (`ENVIRONMENT=development`):
   - Authentication يكون أكثر مرونة
   - CORS يكون مفعلاً
   - Logging يكون مفعلاً

3. **في وضع Production** (`ENVIRONMENT=production`):
   - Authentication يكون صارماً
   - CORS يكون محدوداً
   - Logging يكون محدوداً (INFO level)
   - **يحتاج إعادة بناء Frontend**: `npm run build:prod`

4. **Hot Reload**:
   - Backend: يستخدم `--reload` flag لتحديث التغييرات تلقائياً (Development فقط)
   - Frontend: Vite يدعم Hot Module Replacement (HMR) تلقائياً (Development فقط)

5. **المنافذ الافتراضية:**
   - Backend: `8000`
   - Frontend Dev: `5173` (Development)
   - Frontend Preview: `4173` (Production)
   - PostgreSQL: `5432`
   - Redis: `6379`
   - Neo4j: `7687`

---

## 🎯 الخطوات السريعة (Quick Start)

```powershell
# 1. تشغيل Backend
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System
$env:ENVIRONMENT="development"
$env:DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
$env:REDIS_URL="redis://localhost:6379/0"
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --reload

# 2. في نافذة PowerShell جديدة - تشغيل Frontend
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System\frontend
npm run dev
```

---

## 📚 روابط مفيدة

- [API Documentation](http://localhost:8000/docs) - بعد تشغيل Backend
- [ReDoc](http://localhost:8000/redoc) - بعد تشغيل Backend
- [Landing Page](http://localhost:5173/landing) - بعد تشغيل Frontend
- [Testing Dashboard](http://localhost:5173/testing) - بعد تشغيل Frontend

---

**تم إنشاء هذا الدليل بتاريخ: 2025-12-27**

