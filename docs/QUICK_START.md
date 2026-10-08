# 🚀 دليل البدء السريع | Quick Start Guide

**لغة:** عربي 🇸🇦 | [English](QUICK_START_EN.md)

---

## 📋 المتطلبات الأساسية | Prerequisites

### متطلبات النظام | System Requirements

| المتطلب | الحد الأدنى | الموصى به | عالي الأداء |
|---|---|---|---|
| **RAM** | 4 GB | 16 GB | 32 GB+ |
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **GPU** (اختياري) | - | NVIDIA 6GB+ | NVIDIA 12GB+ |
| **Storage** | 10 GB | 50 GB | 100 GB+ |

### متطلبات البرامج | Software Requirements

```bash
# تحقق من الإصدارات
python --version        # Python 3.9+
pip --version          # pip 21+
docker --version       # Docker 20+ (اختياري)
docker-compose --version  # Docker Compose 2+ (اختياري)
```

**البرامج المطلوبة:**
- ✅ Python 3.9 أو أحدث
- ✅ pip (مدير حزم Python)
- ✅ Git
- ⭐ Ollama (لتشغيل النماذج محلياً)
- ⭐ Docker + Docker Compose (اختياري، للنشر)

---

## 🏃 البدء السريع | Quick Start (5 دقائق)

### الخطوة 1: استنساخ المشروع | Clone Repository

```bash
git clone https://github.com/ahmedmokireldinonline/hermes-agent.git
cd hermes-agent
```

### الخطوة 2: إنشاء بيئة افتراضية | Create Virtual Environment

```bash
# على Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# على Windows
python -m venv .venv
.venv\Scripts\activate
```

### الخطوة 3: تثبيت الحزم | Install Dependencies

```bash
pip install -r requirements.txt
```

### الخطوة 4: إعداد الإعدادات | Setup Configuration

```bash
# انسخ ملف الإعدادات
cp .env.example .env

# يمكنك تعديل .env حسب احتياجاتك
# nano .env  أو استخدم محرر نصوص آخر
```

### الخطوة 5: تشغيل الخادم | Start Server

```bash
# الوضع الافتراضي (MOCK_LLM=true) - لا يحتاج Ollama
uvicorn app.api:app --reload --port 8000

# أو استخدم سكريبت التشغيل
python scripts/start.py
```

### الخطوة 6: اختبر الخادم | Test the Server

```bash
# افتح نافذة terminal جديدة

# تحقق من الصحة
curl http://localhost:8000/health

# أرسل مهمة اختبار
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"input":"ما هو 2+2؟"}'
```

✅ **تم!** المشروع يعمل الآن على `http://localhost:8000`

---

## 🧠 استخدام النماذج المحلية | Using Local Models

### تثبيت Ollama | Install Ollama

1. تحميل من: https://ollama.ai
2. اتبع التعليمات حسب نظام التشغيل
3. تحقق من التثبيت:
   ```bash
   ollama --version
   ```

### تحميل نموذج | Pull a Model

```bash
# اختر حسب جهازك:

# Lite (4GB RAM)
ollama pull qwen:4b
ollama pull qwen:8b

# Balanced (16GB RAM)
ollama pull qwen:14b
ollama pull deepseek-r1:14b

# Quality (32GB+ RAM)
ollama pull qwen:32b
ollama pull deepseek-r1:32b
```

### تفعيل النموذج المحلي | Enable Local Model

تعديل `.env`:

```env
# قبل
MOCK_LLM=true
# OLLAMA_URL=http://localhost:11434

# بعد
MOCK_LLM=false
OLLAMA_URL=http://localhost:11434
DEFAULT_MODEL=qwen:14b
```

### تشغيل Ollama | Start Ollama

```bash
# في نافذة terminal منفصلة
ollama serve
```

### تشغيل التطبيق | Start Application

```bash
# في نافذة terminal أخرى
uvicorn app.api:app --reload --port 8000
```

---

## 🐳 النشر باستخدام Docker | Docker Deployment

### الطريقة السريعة | Quick Deploy

```bash
# بناء وتشغيل
docker-compose up --build

# أو في الخلفية
docker-compose up -d --build
```

### عرض السجلات | View Logs

```bash
docker-compose logs -f hermes-api
```

### إيقاف الخدمة | Stop Service

```bash
docker-compose down
```

---

## 🎮 التفاعل مع API | API Interaction

### 1. إنشاء مهمة | Create Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "اكتب قصة قصيرة عن الذكاء الاصطناعي",
    "idempotency_key": "story-001"
  }'
```

**الرد | Response:**
```json
{
  "id": "task-12345",
  "status": "queued",
  "input": "اكتب قصة قصيرة عن الذكاء الاصطناعي",
  "created_at": "2026-10-08T20:00:00Z"
}
```

### 2. التحقق من حالة المهمة | Check Task Status

```bash
curl http://localhost:8000/tasks/task-12345
```

**الرد | Response:**
```json
{
  "id": "task-12345",
  "status": "succeeded",
  "input": "اكتب قصة قصيرة عن الذكاء الاصطناعي",
  "output": "كان هناك روبوت ذكي...",
  "created_at": "2026-10-08T20:00:00Z",
  "completed_at": "2026-10-08T20:05:30Z"
}
```

### 3. الصحة والإحصائيات | Health & Stats

```bash
# تحقق من صحة النظام
curl http://localhost:8000/health

# احصل على الإحصائيات (إذا كانت متاحة)
curl http://localhost:8000/stats
```

---

## 📊 اختيار الملف الشخصي | Select Profile

اختر الملف الشخصي المناسب حسب جهازك:

### Lite Profile (4-8GB RAM)
```env
# .env
PROFILE=lite
DEFAULT_MODEL=qwen:4b
MAX_TOKENS=512
CONTEXT_LENGTH=2048
```

### Balanced Profile (16GB RAM)
```env
# .env
PROFILE=balanced
DEFAULT_MODEL=qwen:14b
MAX_TOKENS=1024
CONTEXT_LENGTH=4096
```

### Quality Profile (32GB+ RAM)
```env
# .env
PROFILE=quality
DEFAULT_MODEL=qwen:32b
MAX_TOKENS=2048
CONTEXT_LENGTH=8192
```

---

## 🔧 استكشاف الأخطاء | Troubleshooting

### المشكلة: الخادم لا يبدأ | Server won't start

```bash
# تحقق من المنفذ المستخدم
lsof -i :8000  # على Mac/Linux

# استخدم منفذ مختلف
uvicorn app.api:app --port 8001
```

### المشكلة: Ollama لا يتصل | Ollama connection failed

```bash
# تأكد من تشغيل Ollama
ollama serve

# تحقق من الاتصال
curl http://localhost:11434

# تحقق من OLLAMA_URL في .env
```

### المشكلة: استهلاك الذاكرة مرتفع | High memory usage

```env
# .env
BATCH_SIZE=1              # معالجة مهمة واحدة فقط
CONTEXT_LENGTH=1024       # تقليل طول السياق
ENABLE_GPU=false          # تعطيل GPU إذا لزم
```

### المشكلة: حاجز معدل الطلبات | Rate limit errors

```env
# .env
RATE_LIMIT=100            # 100 طلب في الدقيقة
MAX_CONCURRENT_TASKS=5    # مهام متزامنة أقل
```

---

## 📚 الخطوات التالية | Next Steps

### استكشف المزيد | Learn More

1. 📖 اقرأ [دليل الهندسة المعمارية](ARCHITECTURE_AR.md)
2. 🧠 استكشف [دليل النماذج](MODEL_GUIDE_AR.md)
3. 🔐 تعلم [سياسات الأمان](SECURITY_AR.md)
4. 🛠️ اطلع على [API Reference](API_REFERENCE_AR.md)

### التطوير والمساهمة | Development

1. 🔀 إنشاء فرع للميزة الجديدة
2. 📝 اكتب الاختبارات
3. 💬 اطلب merge request
4. ✅ انتظر المراجعة والموافقة

### الحصول على الدعم | Get Help

- 📧 البريد: Ahmedmokireldin.online@gmail.com
- 📱 الهاتف: +201012025650
- 🌐 الموقع: https://Ahmedmokireldin.online
- 🐙 GitHub Issues: https://github.com/ahmedmokireldinonline/hermes-agent/issues

---

## ✅ قائمة التحقق | Checklist

- [ ] Python 3.9+ مثبت
- [ ] المشروع تم استنساخه
- [ ] البيئة الافتراضية نشطة
- [ ] الحزم مثبتة (requirements.txt)
- [ ] ملف .env تم إنشاؤه
- [ ] الخادم يعمل على المنفذ 8000
- [ ] curl يعيد استجابة صحيحة
- [ ] (اختياري) Ollama مثبت وتشغيل نموذج

---

**تهانينا! 🎉 أنت جاهز للبدء مع Hermes Agent**

إذا واجهت أي مشاكل، راجع قسم الاستكشاف أو تواصل معنا.

آخر تحديث: 8 أكتوبر 2026
