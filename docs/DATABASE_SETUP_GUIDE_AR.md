# 🗄️ دليل إعداد قواعد البيانات - AMAS

## 📋 المشكلة الحالية

من صفحة الاختبارات:
- ❌ **Database Disconnected** - PostgreSQL غير متصل
- ❌ **Redis Disconnected** - Redis غير متصل  
- ❌ **Neo4j Disconnected** - Neo4j غير متصل
- ⚠️ **System Status: UNHEALTHY** - بسبب قواعد البيانات غير المتصلة

---

## ✅ الحلول

### الطريقة 1: استخدام Docker Compose (موصى به)

#### تشغيل جميع قواعد البيانات:

```bash
# تشغيل PostgreSQL + Redis + Neo4j
docker-compose up -d postgres redis neo4j
```

#### التحقق من الحالة:

```bash
# عرض حالة الحاويات
docker-compose ps

# عرض Logs
docker-compose logs postgres redis neo4j
```

---

### الطريقة 2: التثبيت اليدوي

#### 1. PostgreSQL

**Windows:**
```powershell
# تحميل وتثبيت PostgreSQL من:
# https://www.postgresql.org/download/windows/

# بعد التثبيت، إنشاء قاعدة البيانات:
psql -U postgres
CREATE DATABASE amas;
CREATE USER amas_user WITH PASSWORD 'amas_password';
GRANT ALL PRIVILEGES ON DATABASE amas TO amas_user;
\q
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# تشغيل PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# إنشاء قاعدة البيانات
sudo -u postgres psql
CREATE DATABASE amas;
CREATE USER amas_user WITH PASSWORD 'amas_password';
GRANT ALL PRIVILEGES ON DATABASE amas TO amas_user;
\q
```

#### 2. Redis

**Windows:**
```powershell
# تحميل Redis من:
# https://github.com/microsoftarchive/redis/releases

# أو استخدام WSL:
wsl
sudo apt install redis-server
redis-server
```

**Linux:**
```bash
sudo apt update
sudo apt install redis-server

# تشغيل Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# التحقق
redis-cli ping
# يجب أن يعود: PONG
```

#### 3. Neo4j

**Windows:**
```powershell
# تحميل Neo4j Desktop من:
# https://neo4j.com/download/

# أو استخدام Docker:
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/amas_password neo4j:latest
```

**Linux:**
```bash
# استخدام Docker (موصى به)
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/amas_password \
  neo4j:latest

# أو تثبيت محلي
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j
sudo systemctl start neo4j
```

---

## 🔧 إعداد متغيرات البيئة

بعد تشغيل قواعد البيانات، تأكد من تحديث `.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql://amas_user:amas_password@localhost:5432/amas
POSTGRES_PASSWORD=amas_password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=amas_password
```

---

## ✅ التحقق من الاتصال

### 1. PostgreSQL:
```bash
psql -U amas_user -d amas -h localhost
# إذا نجح، اكتب \q للخروج
```

### 2. Redis:
```bash
redis-cli ping
# يجب أن يعود: PONG
```

### 3. Neo4j:
```bash
# افتح المتصفح:
http://localhost:7474

# أو استخدم cypher-shell:
docker exec -it neo4j cypher-shell -u neo4j -p amas_password
```

---

## 🚀 تشغيل سريع (Docker Compose)

### الطريقة السريعة (موصى به):

**Windows:**
```cmd
scripts\start_databases.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start_databases.sh
./scripts/start_databases.sh
```

### الطريقة اليدوية:

```bash
# 1. تشغيل قواعد البيانات فقط
docker-compose up -d postgres redis neo4j

# 2. الانتظار 15 ثانية للتأكد من بدء التشغيل
timeout /t 15  # Windows
sleep 15       # Linux

# 3. التحقق من الحالة
docker-compose ps

# 4. إعادة تشغيل Backend
set ENVIRONMENT=production
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000
```

---

## 📊 النتيجة المتوقعة

بعد تشغيل قواعد البيانات وإعادة تشغيل Backend:

- ✅ **Database Connected** - PostgreSQL متصل
- ✅ **Redis Connected** - Redis متصل
- ✅ **Neo4j Connected** - Neo4j متصل
- ✅ **System Status: HEALTHY** - النظام صحي

---

## 🔍 استكشاف الأخطاء

### PostgreSQL لا يعمل:

```bash
# Windows
netstat -ano | findstr :5432

# Linux
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Redis لا يعمل:

```bash
# Windows
netstat -ano | findstr :6379

# Linux
sudo systemctl status redis-server
sudo systemctl start redis-server
```

### Neo4j لا يعمل:

```bash
# التحقق من Docker
docker ps | grep neo4j

# أو التحقق من المنفذ
netstat -ano | findstr :7687
```

---

## 📝 ملاحظات مهمة

1. **قواعد البيانات اختيارية**: النظام يعمل بدونها، لكن بعض الميزات لن تعمل (مثل حفظ المهام في قاعدة البيانات)

2. **في وضع Development**: يمكن العمل بدون قواعد البيانات للتطوير السريع

3. **في وضع Production**: يجب تشغيل جميع قواعد البيانات للحصول على أفضل أداء

---

**آخر تحديث**: 2025-12-28

