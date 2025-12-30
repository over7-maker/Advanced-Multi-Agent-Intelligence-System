# 🚀 دليل نشر الإنتاج الكامل - AMAS

## 📋 المشكلة الحالية

إذا كنت لا ترى التطويرات الأخيرة في الإنتاج، فهذا يعني أن:
1. **البناء (Build) قديم** - يحتاج إلى إعادة بناء
2. **الخدمات لا تعمل على المنافذ الصحيحة**
3. **المسارات (Routes) غير متاحة**

## ✅ الحل السريع

### الخطوة 1: إعادة بناء Frontend بجميع التطويرات الأخيرة

#### على Windows:
```cmd
scripts\rebuild_frontend_production.bat
```

#### على Linux/Mac:
```bash
chmod +x scripts/rebuild_frontend_production.sh
./scripts/rebuild_frontend_production.sh
```

### الخطوة 2: تشغيل الخدمات في الإنتاج

#### على Windows:
```cmd
scripts\start_production_services.bat
```

#### على Linux/Mac:
```bash
chmod +x scripts/start_production_services.sh
./scripts/start_production_services.sh
```

## 🌐 الوصول إلى الصفحات

بعد التشغيل، ستكون جميع الصفحات متاحة على:

- **Frontend Preview**: http://localhost:4173
- **Landing Page**: http://localhost:4173/landing ✅
- **Testing Dashboard**: http://localhost:4173/testing ✅
- **Dashboard**: http://localhost:4173/dashboard
- **Tasks**: http://localhost:4173/tasks
- **Agents**: http://localhost:4173/agents
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 الطريقة اليدوية

### 1. إعادة بناء Frontend يدوياً

```bash
cd frontend

# تنظيف البناء القديم
rm -rf dist  # Linux/Mac
# أو
rmdir /s /q dist  # Windows

# تثبيت التبعيات (إذا لزم الأمر)
npm install

# بناء للإنتاج
npm run build:prod
```

### 2. تشغيل Frontend Preview

```bash
cd frontend
npm run preview
```

سيتم تشغيل Frontend على: **http://localhost:4173**

### 3. تشغيل Backend

```bash
# في مجلد المشروع الرئيسي
set ENVIRONMENT=production
set DATABASE_URL=postgresql://postgres:amas_password@localhost:5432/amas
set REDIS_URL=redis://localhost:6379/0
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

## 📝 ملاحظات مهمة

### 1. **المنافذ (Ports)**
- **Frontend Dev**: 5173 (npm run dev)
- **Frontend Preview/Production**: 4173 (npm run preview)
- **Backend**: 8000

### 2. **الفرق بين Dev و Production**

| الوضع | الأمر | المنفذ | الاستخدام |
|------|------|--------|----------|
| Development | `npm run dev` | 5173 | التطوير مع Hot Reload |
| Production Preview | `npm run preview` | 4173 | معاينة البناء النهائي |
| Production Build | `npm run build:prod` | - | إنشاء ملفات البناء فقط |

### 3. **المسارات المتاحة**

جميع المسارات التالية متاحة بعد إعادة البناء:

- ✅ `/landing` - صفحة الهبوط (Landing Page)
- ✅ `/testing` - لوحة الاختبارات (Testing Dashboard)
- ✅ `/dashboard` - لوحة التحكم
- ✅ `/tasks` - قائمة المهام
- ✅ `/tasks/create` - إنشاء مهمة جديدة
- ✅ `/agents` - قائمة الوكلاء
- ✅ `/integrations` - التكاملات
- ✅ `/health` - حالة النظام
- ✅ `/workflow-builder` - منشئ سير العمل

### 4. **متى تحتاج إلى إعادة البناء؟**

يجب إعادة بناء Frontend عندما:
- ✅ أضفت مكونات جديدة
- ✅ غيرت المسارات (Routes)
- ✅ أضفت صفحات جديدة
- ✅ غيرت الإعدادات (vite.config.ts)
- ✅ أضفت مكتبات جديدة
- ✅ غيرت ملفات CSS أو Assets

## 🔍 استكشاف الأخطاء

### المشكلة: صفحة `/landing` لا تعمل

**الحل:**
1. تأكد من إعادة البناء: `scripts\rebuild_frontend_production.bat`
2. تأكد من تشغيل Preview: `cd frontend && npm run preview`
3. تحقق من أن المسار صحيح: `http://localhost:4173/landing` (بدون //)

### المشكلة: صفحة `/testing` لا تعمل

**الحل:**
1. تأكد من وجود المكون: `frontend/src/components/Testing/TestingDashboard.tsx`
2. تأكد من إعادة البناء
3. تحقق من أن المسار في App.tsx صحيح

### المشكلة: لا أرى التطويرات الأخيرة

**الحل:**
1. **أعد البناء**: `scripts\rebuild_frontend_production.bat`
2. **أوقف Preview القديم** وأعد تشغيله
3. **امسح Cache المتصفح**: Ctrl+Shift+Delete

### المشكلة: Port 4173 مستخدم

**الحل:**
```bash
# Windows
netstat -ano | findstr :4173
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:4173 | xargs kill -9
```

## 📊 التحقق من البناء

بعد إعادة البناء، تحقق من:

```bash
cd frontend/dist

# يجب أن تجد:
✅ index.html
✅ assets/ (مجلد)
✅ vite.svg (اختياري)
```

## 🎯 سكريبتات متاحة

### Windows:
- `scripts\rebuild_frontend_production.bat` - إعادة بناء Frontend
- `scripts\start_production_services.bat` - تشغيل جميع الخدمات

### Linux/Mac:
- `scripts/rebuild_frontend_production.sh` - إعادة بناء Frontend
- `scripts/start_production_services.sh` - تشغيل جميع الخدمات

## 🔄 سير العمل الموصى به

1. **تطوير** → `npm run dev` (port 5173)
2. **اختبار** → `npm run build && npm run preview` (port 4173)
3. **إنتاج** → `npm run build:prod` ثم نشر dist/

## 📞 الدعم

إذا استمرت المشاكل:
1. تحقق من Logs: `logs/backend.log` و `logs/frontend.log`
2. تحقق من أن جميع المكونات موجودة في `frontend/src/components/`
3. تحقق من أن المسارات في `App.tsx` صحيحة

---

**آخر تحديث**: 2025-12-27
**الإصدار**: 1.0.0

