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
| **نظام التشغيل** | Linux/Mac/Windows | Ubuntu 20.04+ | Ubuntu 22.04+ |

### متطلبات البرامج | Software Requirements

تأكد من تثبيت هذه البرامج:

```bash
python --version    # Python 3.9+
pip --version       # pip 21+
docker --version    # Docker 20.10+
git --version       # Git 2.25+
```

---

## 🏃 البدء السريع (5 دقائق) | Quick Start (5 Minutes)

### الخطوة 1️⃣: استنساخ المشروع | Clone Repository

```bash
git clone https://github.com/ahmedmokireldinonline/hermes-agent.git
cd hermes-agent
```

### الخطوة 2️⃣: إنشاء بيئة افتراضية | Create Virtual Environment

```bash
# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### الخطوة 3️⃣: تثبيت الحزم | Install Dependencies

```bash
pip install -r requirements.txt
```

### الخطوة 4️⃣: إعداد الإعدادات | Setup Configuration

```bash
cp .env.example .env
```

**ملفات الإعدادات المهمة:**
- `MOCK_LLM=true` - للاختبار السريع (بدون Ollama)
- `PORT=8000` - منفذ الخادم
- `DATABASE_URL=sqlite:///./hermes.db` - قاعدة البيانات

### الخطوة 5️⃣: تشغيل الخادم | Start Server

```bash
uvicorn app.api:app --reload --port 8000
```

ستظهر رسالة مشابهة لهذه:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### الخطوة 6️⃣: اختبر الخادم | Test the Server

فتح نافذة طرفية جديدة واختبر:

```bash
# اختبر صحة الخادم
curl http://localhost:8000/health

# أرسل مهمة
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"input":"ما هو 2+2؟"}'
```

---

## 🧠 استخدام النماذج المحلية | Using Local Models

### خطوة 1️⃣: تثبيت Ollama | Install Ollama

```bash
# الموقع الرسمي
https://ollama.ai/

# أو باستخدام Package Manager
# على Ubuntu:
curl https://ollama.ai/install.sh | sh

# على Mac:
brew install ollama

# على Windows:
# حمّل المثبت من الموقع الرسمي
```

### خطوة 2️⃣: اختيار نموذج | Choose a Model

اختر حسب إمكانيات جهازك:

**للأجهزة الضعيفة (4 GB RAM) - Lite 🟢:**
```bash
ollama pull qwen:8b
ollama run qwen:8b
```

**للأجهزة المتوسطة (16 GB RAM) - Balanced 🟡:**
```bash
ollama pull qwen:14b
ollama run qwen:14b
```

**للأجهزة القوية (32+ GB RAM) - Quality 🔴:**
```bash
ollama pull qwen:32b
ollama run qwen:32b
```

### خطوة 3️⃣: تكوين Hermes | Configure Hermes

عدّل ملف `.env`:

```env
# تفعيل النموذج المحلي
MOCK_LLM=false
OLLAMA_URL=http://localhost:11434
DEFAULT_MODEL=qwen:14b
PROFILE=balanced
```

### خطوة 4️⃣: تشغيل Ollama | Start Ollama

في نافذة طرفية منفصلة:

```bash
ollama serve
```

### خطوة 5️⃣: إعادة تشغيل Hermes | Restart Hermes

```bash
# أوقف الخادم السابق (Ctrl+C)
# ثم أعد التشغيل
uvicorn app.api:app --reload --port 8000
```

---

## 🐳 النشر باستخدام Docker | Docker Deployment

### جميع الخدمات في حاوية واحدة | All-in-One Setup

```bash
# تنزيل الصور وتشغيل الخدمات
docker-compose up --build

# في نافذة أخرى، اختبر:
curl http://localhost:8000/health
```

**ملاحظات:**
- سيتم تشغيل FastAPI
- سيتم تشغيل Redis (إذا كان مفعلاً)
- سيتم تشغيل PostgreSQL (خياري)
- سيتم تشغيل Ollama (خياري)

### إيقاف الخدمات | Stop Services

```bash
docker-compose down
```

---

## 📊 نماذج موصى بها | Recommended Models

### للاختبار السريع | For Quick Testing
```bash
ollama pull mistral:latest
# الحجم: ~4 GB
# الأداء: متوسط
# الوقت: ~2 دقيقة
```

### للإنتاج | For Production
```bash
ollama pull qwen:14b
# الحجم: ~9 GB
# الأداء: ممتاز
# الوقت: ~5 دقائق
```

### لأداء عالي | For High Performance
```bash
ollama pull qwen:32b
# الحجم: ~18 GB
# الأداء: ممتاز جداً
# الوقت: ~10 دقائق
```

---

## 🔒 الأمان الأساسي | Basic Security

⚠️ **هام جداً:**

```env
# 1. فعّل مفتاح API
API_KEYS=your-secret-key-here

# 2. استخدم HTTPS في الإنتاج
# لا تفعل localhost العام على الإنترنت

# 3. استخدم متغيرات البيئة
# لا تضع كلمات المرور في الكود
```

---

## 📁 هيكل المشروع | Project Structure

```
hermes-agent/
├── app/                    # تطبيق FastAPI الرئيسي
│   ├── api.py             # نقاط النهاية
│   ├── agent.py           # منطق الوكيل
│   ├── db.py              # نماذج قاعدة البيانات
│   ├── llm.py             # واجهة LLM
│   ├── tools.py           # الأدوات المتاحة
│   ├── skills.py          # نظام المهارات
│   └── worker.py          # عامل Redis
├── config/                # ملفات الإعدادات
│   ├── models.open.yaml   # ملفات النماذج
│   └── profiles.yaml      # الملفات الشخصية
├── docs/                  # التوثيق
│   ├── QUICK_START_AR.md  # هذا الملف
│   ├── ARCHITECTURE_AR.md # الهندسة المعمارية
│   ├── SECURITY_AR.md     # سياسات الأمان
│   ├── MODEL_GUIDE_AR.md  # دليل النماذج
│   └── OPEN_MODELS_REFERENCE.html
├── scripts/               # نصوص مساعدة
│   ├── pull-models.sh     # تحميل النماذج
│   ├── setup-env.sh       # إعداد البيئة
│   └── start.sh           # تشغيل المشروع
├── web/                   # واجهة المستخدم
│   ├── dashboard.html     # لوحة التحكم
│   ├── landing.html       # الصفحة الرئيسية
│   └── assets/            # الصور والأيقونات
├── tests/                 # الاختبارات
├── workspace/             # مساحة العمل المقيدة
├── requirements.txt       # المكتبات المطلوبة
├── docker-compose.yml     # إعدادات Docker
└── README.md              # ملف readme
```

---

## 🐛 استكشاف الأخطاء | Troubleshooting

### المشكلة: الخادم لا ينطلق
```bash
# تحقق من المنفذ
lsof -i :8000

# غيّر المنفذ
uvicorn app.api:app --port 8001
```

### المشكلة: Ollama لا يتصل
```bash
# تحقق من تشغيل Ollama
curl http://localhost:11434

# أعد تشغيل Ollama
ollama serve
```

### المشكلة: خطأ في الذاكرة
```bash
# استخدم نموذج أصغر
ollama pull mistral:latest

# أو زيادة RAM المتاح
```

---

## ✅ قائمة التحقق | Checklist

- [ ] Python 3.9+ مثبت
- [ ] Git مثبت
- [ ] المشروع تم استنساخه
- [ ] البيئة الافتراضية تم إنشاؤها
- [ ] الحزم تم تثبيتها
- [ ] ملف .env تم إنشاؤه
- [ ] الخادم يعمل بدون أخطاء
- [ ] `/health` ترد بـ 200 OK
- [ ] Ollama مثبت (اختياري)
- [ ] نموذج تم تحميله (اختياري)

---

## 📞 التواصل والدعم | Contact & Support

إذا واجهت مشاكل:

📧 **البريد الإلكتروني:**  
Ahmedmokireldin.online@gmail.com

📱 **الهاتف:**  
+201012025650 أو +201006334062

🌐 **الموقع:**  
https://Ahmedmokireldin.online

---

## 📚 الخطوات التالية | Next Steps

1. 📖 اقرأ [دليل الهندسة المعمارية](ARCHITECTURE_AR.md)
2. 🧠 استكشف [دليل النماذج](MODEL_GUIDE_AR.md)
3. 🔐 تعلم [سياسات الأمان](SECURITY_AR.md)
4. 👤 تعرف على [مالك المشروع](../OWNER.md)

---

**تهانينا! 🎉 أنت جاهز للبدء مع Hermes Agent**

**آخر تحديث:** 8 أكتوبر 2026  
**الإصدار:** 1.0
