# 🔧 إصلاح مشاكل الإنتاج - Production Fixes

## المشاكل المكتشفة

### 1. ❌ خطأ في متغير البيئة
**الخطأ:**
```
Value error, Environment must be one of ['development', 'testing', 'staging', 'production'] 
[type=value_error, input_value='production ', input_type=str]
```

**السبب:** وجود مسافة زائدة في نهاية `ENVIRONMENT=production `

**الحل:** تأكد من عدم وجود مسافات زائدة عند تعيين المتغيرات.

### 2. ❌ جميع طلبات API تعطي 404
**الخطأ:**
```
GET http://localhost:4173/api/v1/me 404 (Not Found)
POST http://localhost:4173/api/v1/tasks 404 (Not Found)
```

**السبب:** Vite Preview proxy لا يوجه الطلبات بشكل صحيح إلى Backend.

**الحل:** استخدم أحد الحلول التالية:

---

## ✅ الحلول

### الحل 1: استخدام Backend مباشرة (موصى به)

بدلاً من استخدام Vite Preview proxy، استخدم Backend مباشرة:

1. **شغّل Backend على port 8000:**
```cmd
set ENVIRONMENT=production
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

2. **شغّل Frontend Preview على port 4173:**
```cmd
cd frontend
npm run preview
```

3. **استخدم Backend مباشرة للـ API:**
   - افتح `frontend/src/services/api.ts`
   - غيّر `baseURL` إلى:
   ```typescript
   baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
   ```

### الحل 2: إصلاح Vite Proxy

تم تحديث `frontend/vite.config.ts` لإصلاح proxy. تأكد من:

1. **إعادة بناء Frontend:**
```cmd
cd frontend
npm run build:prod
```

2. **إعادة تشغيل Preview:**
```cmd
npm run preview
```

### الحل 3: استخدام Environment Variable

أنشئ ملف `.env` في مجلد `frontend/`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

ثم أعد بناء Frontend:
```cmd
cd frontend
npm run build:prod
npm run preview
```

---

## 🔍 التحقق من الإصلاحات

### 1. تحقق من Backend:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

### 2. تحقق من Frontend:
افتح المتصفح وافحص Console:
- يجب ألا ترى أخطاء 404
- يجب أن تعمل جميع طلبات API

### 3. تحقق من متغيرات البيئة:
```cmd
echo %ENVIRONMENT%
```
يجب أن يكون: `production` (بدون مسافات)

---

## 📝 ملاحظات مهمة

1. **Vite Preview Proxy**: قد لا يعمل بشكل موثوق في بعض الحالات. استخدم Backend مباشرة للحصول على أفضل أداء.

2. **CORS**: تأكد من أن Backend يسمح بـ CORS من `http://localhost:4173`

3. **Environment Variables**: تأكد من عدم وجود مسافات زائدة في نهاية القيم.

---

## 🚀 الخطوات السريعة للإصلاح

```cmd
REM 1. إيقاف جميع الخدمات
taskkill /F /IM python.exe
taskkill /F /IM node.exe

REM 2. إصلاح baseURL في api.ts
REM افتح frontend/src/services/api.ts
REM غيّر baseURL إلى: 'http://localhost:8000/api/v1'

REM 3. إعادة بناء Frontend
cd frontend
npm run build:prod

REM 4. تشغيل Backend (في نافذة منفصلة)
cd ..
set ENVIRONMENT=production
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000

REM 5. تشغيل Frontend Preview (في نافذة منفصلة)
cd frontend
npm run preview
```

---

**آخر تحديث**: 2025-12-28

