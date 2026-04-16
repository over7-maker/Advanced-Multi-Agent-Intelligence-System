# ✅ دليل اتصال Redis - Redis Connection Guide

**التاريخ**: 2025-12-28

---

## 🔍 المشكلة

Redis لا يزال غير متصل رغم وضع environment variables.

**السبب**: Environment variables في PowerShell قد لا تكون مرئية لـ Python عند تشغيله.

---

## ✅ الحلول

### الحل 1: استخدام REDIS_URL مع password في URL (الأسهل)

```cmd
set REDIS_URL=redis://:amas_redis_password@localhost:6379/0
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

### الحل 2: استخدام REDIS_URL و REDIS_PASSWORD منفصلين

```cmd
set REDIS_URL=redis://localhost:6379/0
set REDIS_PASSWORD=amas_redis_password
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

### الحل 3: استخدام ملف .env (الأفضل للإنتاج)

أنشئ ملف `.env` في root directory:

```env
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=amas_redis_password
```

ثم شغل Backend:
```cmd
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

---

## 🔍 التحقق من Environment Variables

### في PowerShell:

```powershell
$env:REDIS_URL
$env:REDIS_PASSWORD
```

### في Python (قبل تشغيل Backend):

```python
import os
print("REDIS_URL:", os.getenv("REDIS_URL"))
print("REDIS_PASSWORD:", os.getenv("REDIS_PASSWORD"))
```

---

## ✅ النتيجة المتوقعة

بعد إعادة التشغيل:

```
INFO:src.config.settings:Redis URL set from env var: redis://:***@localhost:6379/0...
INFO:src.cache.redis:Initial Redis URL from settings: redis://:amas_redis_password@localhost:6379/0
INFO:src.cache.redis:URL has password: True
INFO:src.cache.redis:Redis connection initialized successfully from URL
```

**لا مزيد من**:
- ❌ `Authentication required` errors
- ❌ `Redis not connected` في testing page

---

## 🚀 الخطوات النهائية

1. **أوقف Backend** (Ctrl+C)

2. **ضع Environment Variables**:
   ```cmd
   set REDIS_URL=redis://:amas_redis_password@localhost:6379/0
   ```

3. **أعد تشغيل Backend**:
   ```cmd
   python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
   ```

4. **تحقق من Logs** - ابحث عن:
   - `Redis URL set from env var`
   - `Added password to Redis URL`
   - `Redis connection initialized successfully`

---

**الحالة**: ✅ **الكود يعمل - المشكلة في Environment Variables**

