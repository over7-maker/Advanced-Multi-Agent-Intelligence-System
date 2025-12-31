# 🔧 إصلاح مشكلة Docker Network Conflict

## المشكلة

```
failed to create network advanced-multi-agent-intelligence-system_amas-network: 
Error response from daemon: invalid pool request: Pool overlaps with other one on this address space
```

**السبب**: Docker network موجود بالفعل ويتعارض مع network جديد.

---

## ✅ الحل السريع

### الطريقة 1: استخدام سكريبت الإصلاح (موصى به)

**Windows:**
```cmd
scripts\fix_docker_network.bat
scripts\start_databases.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/fix_docker_network.sh
chmod +x scripts/start_databases.sh
./scripts/fix_docker_network.sh
./scripts/start_databases.sh
```

### الطريقة 2: يدوياً

```bash
# 1. إزالة الشبكة المتعارضة
docker network rm advanced-multi-agent-intelligence-system_amas-network

# 2. تنظيف الشبكات غير المستخدمة
docker network prune -f

# 3. تشغيل قواعد البيانات
docker-compose up -d postgres redis neo4j
```

---

## 🔍 التحقق من الحالة

بعد الإصلاح:

```bash
# التحقق من الشبكات
docker network ls | grep amas-network

# التحقق من الحاويات
docker-compose ps postgres redis neo4j
```

---

## 📝 ملاحظات

1. **السكريبتات المحدثة**: تم تحديث `start_databases.bat` و `start_databases.sh` للتعامل مع هذه المشكلة تلقائياً

2. **إذا استمرت المشكلة**: 
   - أعد تشغيل Docker Desktop
   - أو استخدم: `docker network prune -f`

---

**آخر تحديث**: 2025-12-28

