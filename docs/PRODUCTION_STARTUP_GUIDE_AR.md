# 🚀 دليل تشغيل AMAS في وضع الإنتاج (Production Mode)

## 📋 نظرة عامة

هذا الدليل يوضح كيفية تشغيل **Frontend** و **Backend** في وضع الإنتاج مع جميع التطويرات الأخيرة.

---

## ⚡ الطريقة السريعة (موصى بها)

### Windows:

```cmd
REM 1. إعادة بناء Frontend بجميع التطويرات الأخيرة
scripts\rebuild_frontend_production.bat

REM 2. تشغيل جميع الخدمات (Backend + Frontend)
scripts\start_production_services.bat
```

### Linux/Mac:

```bash
# 1. إعادة بناء Frontend بجميع التطويرات الأخيرة
chmod +x scripts/rebuild_frontend_production.sh
./scripts/rebuild_frontend_production.sh

# 2. تشغيل جميع الخدمات (Backend + Frontend)
chmod +x scripts/start_production_services.sh
./scripts/start_production_services.sh
```

---

## 🔧 الطريقة اليدوية (خطوة بخطوة)

### الخطوة 1: إعداد متغيرات البيئة

#### Windows (CMD):
```cmd
set ENVIRONMENT=production
set DATABASE_URL=postgresql://postgres:amas_password@localhost:5432/amas
set REDIS_URL=redis://localhost:6379/0
```

#### Windows (PowerShell):
```powershell
$env:ENVIRONMENT="production"
$env:DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
$env:REDIS_URL="redis://localhost:6379/0"
```

#### Linux/Mac:
```bash
export ENVIRONMENT=production
export DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
export REDIS_URL="redis://localhost:6379/0"
```

### الخطوة 2: إعادة بناء Frontend

```bash
cd frontend

# تنظيف البناء القديم
rm -rf dist  # Linux/Mac
# أو
rmdir /s /q dist  # Windows

# بناء للإنتاج
npm run build:prod
```

### الخطوة 3: تشغيل Backend

#### في نافذة منفصلة:

**Windows (CMD):**
```cmd
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System
set ENVIRONMENT=production
set DATABASE_URL=postgresql://postgres:amas_password@localhost:5432/amas
set REDIS_URL=redis://localhost:6379/0
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

**Windows (PowerShell):**
```powershell
cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System
$env:ENVIRONMENT="production"
$env:DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
$env:REDIS_URL="redis://localhost:6379/0"
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

**Linux/Mac:**
```bash
cd /path/to/Advanced-Multi-Agent-Intelligence-System
export ENVIRONMENT=production
export DATABASE_URL="postgresql://postgres:amas_password@localhost:5432/amas"
export REDIS_URL="redis://localhost:6379/0"
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

**النتيجة المتوقعة:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### الخطوة 4: تشغيل Frontend Preview

#### في نافذة منفصلة:

```bash
cd frontend
npm run preview
```

**النتيجة المتوقعة:**
```
  ➜  Local:   http://localhost:4173/
  ➜  Network: http://192.168.x.x:4173/
```

---

## 🎯 الطريقة التلقائية (نوافذ منفصلة)

### Windows PowerShell:

#### تشغيل Backend في نافذة منفصلة:
```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:ENVIRONMENT='production'; `$env:DATABASE_URL='postgresql://postgres:amas_password@localhost:5432/amas'; `$env:REDIS_URL='redis://localhost:6379/0'; cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System; Write-Host '🚀 Starting AMAS Backend (Production)...' -ForegroundColor Cyan; python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000"
```

#### تشغيل Frontend Preview في نافذة منفصلة:
```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System\frontend; Write-Host '🚀 Starting AMAS Frontend Preview (Production)...' -ForegroundColor Cyan; npm run preview"
```

---

## 📊 الفرق بين Development و Production

| الميزة | Development | Production |
|--------|------------|------------|
| **المنفذ** | 5173 | 4173 |
| **الأمر** | `npm run dev` | `npm run preview` |
| **Hot Reload** | ✅ نعم | ❌ لا |
| **Source Maps** | ✅ مفعّل | ⚠️ محدود |
| **Optimization** | ❌ لا | ✅ نعم |
| **Build Required** | ❌ لا | ✅ نعم |
| **Performance** | أبطأ | أسرع |

---

## 🌐 الوصول إلى الخدمات

بعد التشغيل، ستكون جميع الصفحات متاحة على:

### Frontend (Port 4173):
- ✅ **Landing Page**: http://localhost:4173/landing
- ✅ **Testing Dashboard**: http://localhost:4173/testing
- ✅ **Dashboard**: http://localhost:4173/dashboard
- ✅ **Tasks**: http://localhost:4173/tasks
- ✅ **Agents**: http://localhost:4173/agents
- ✅ **Integrations**: http://localhost:4173/integrations
- ✅ **Health**: http://localhost:4173/health
- ✅ **Workflow Builder**: http://localhost:4173/workflow-builder

### Backend (Port 8000):
- ✅ **API**: http://localhost:8000
- ✅ **API Documentation**: http://localhost:8000/docs
- ✅ **ReDoc**: http://localhost:8000/redoc
- ✅ **Health Check**: http://localhost:8000/health

---

## ✅ التحقق من حالة الخدمات

### التحقق من Backend:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
```

**Linux/Mac:**
```bash
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

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "http://localhost:4173" -UseBasicParsing
```

**Linux/Mac:**
```bash
curl http://localhost:4173
```

---

## 🔍 استكشاف الأخطاء

### المشكلة: Backend لا يعمل

1. **تحقق من قاعدة البيانات:**
   ```powershell
   # Windows
   psql -U postgres -d amas -h localhost
   ```

2. **تحقق من Redis:**
   ```powershell
   # Windows
   redis-cli ping
   ```

3. **تحقق من المتغيرات البيئية:**
   ```powershell
   # Windows PowerShell
   $env:ENVIRONMENT
   $env:DATABASE_URL
   $env:REDIS_URL
   ```

4. **تحقق من المنافذ:**
   ```powershell
   # Windows
   netstat -ano | findstr :8000
   ```

### المشكلة: Frontend لا يعمل

1. **تأكد من إعادة البناء:**
   ```bash
   cd frontend
   npm run build:prod
   ```

2. **تحقق من وجود ملفات البناء:**
   ```bash
   cd frontend
   ls dist  # Linux/Mac
   dir dist  # Windows
   ```
   يجب أن تجد: `index.html` و `assets/`

3. **تحقق من المنافذ:**
   ```powershell
   # Windows
   netstat -ano | findstr :4173
   ```

4. **امسح Cache وأعد البناء:**
   ```bash
   cd frontend
   rm -rf dist node_modules/.vite
   npm run build:prod
   ```

### المشكلة: صفحة `/landing` لا تعمل

1. **تأكد من إعادة البناء:**
   ```bash
   scripts\rebuild_frontend_production.bat
   ```

2. **تأكد من URL الصحيح:**
   - ✅ **صحيح**: http://localhost:4173/landing
   - ❌ **خطأ**: http://localhost:4173//landing (لا تستخدم //)

3. **أعد تشغيل Preview:**
   ```bash
   cd frontend
   npm run preview
   ```

---

## 🛑 إيقاف الخدمات

### إيقاف Backend:
- اضغط `Ctrl + C` في نافذة Backend

### إيقاف Frontend:
- اضغط `Ctrl + C` في نافذة Frontend Preview

### إيقاف جميع العمليات (Windows PowerShell):

```powershell
# إيقاف جميع عمليات Python (Backend)
Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force

# إيقاف جميع عمليات Node (Frontend)
Get-Process | Where-Object { $_.ProcessName -eq "node" } | Stop-Process -Force
```

---

## 📝 ملاحظات مهمة

### 1. ترتيب التشغيل
- ✅ **ابدأ بـ Backend أولاً** - Frontend يحتاج إلى الاتصال بـ Backend API
- ✅ **ثم شغّل Frontend Preview** - بعد التأكد من أن Backend يعمل

### 2. في وضع Production:
- ✅ **Authentication** يكون صارماً
- ✅ **CORS** يكون محدوداً
- ✅ **Logging** يكون محدوداً (INFO level)
- ✅ **Performance** يكون محسّناً
- ❌ **Hot Reload** غير متاح (يحتاج إعادة بناء)

### 3. عند إجراء تغييرات:
إذا قمت بتعديل أي ملف في Frontend:
1. أعد البناء: `scripts\rebuild_frontend_production.bat`
2. أعد تشغيل Preview: `cd frontend && npm run preview`

### 4. المنافذ الافتراضية:
- **Backend**: `8000`
- **Frontend Preview**: `4173`
- **Frontend Dev**: `5173` (للتطوير فقط)
- **PostgreSQL**: `5432`
- **Redis**: `6379`
- **Neo4j**: `7687`

---

## 🎯 سكريبتات متاحة

### Windows:
- ✅ `scripts\rebuild_frontend_production.bat` - إعادة بناء Frontend
- ✅ `scripts\start_production_services.bat` - تشغيل جميع الخدمات

### Linux/Mac:
- ✅ `scripts/rebuild_frontend_production.sh` - إعادة بناء Frontend
- ✅ `scripts/start_production_services.sh` - تشغيل جميع الخدمات

---

## 📚 روابط مفيدة

- [API Documentation](http://localhost:8000/docs) - بعد تشغيل Backend
- [ReDoc](http://localhost:8000/redoc) - بعد تشغيل Backend
- [Landing Page](http://localhost:4173/landing) - بعد تشغيل Frontend
- [Testing Dashboard](http://localhost:4173/testing) - بعد تشغيل Frontend

---

## 🎉 ملخص سريع

```bash
# 1. إعادة بناء Frontend
scripts\rebuild_frontend_production.bat

# 2. تشغيل Backend (في نافذة منفصلة)
set ENVIRONMENT=production
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000

# 3. تشغيل Frontend Preview (في نافذة منفصلة)
cd frontend
npm run preview

# 4. الوصول
# Frontend: http://localhost:4173/landing
# Backend: http://localhost:8000/docs
```

---

**تم إنشاء هذا الدليل بتاريخ: 2025-12-27**  
**آخر تحديث: 2025-12-27**

