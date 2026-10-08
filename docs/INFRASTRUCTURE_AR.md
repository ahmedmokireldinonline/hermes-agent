# دليل البنية التحتية - Hermes Agent

هذا الدليل يوفر المتطلبات الكاملة والإرشادات التشغيلية لتشغيل منصة Hermes Agent في بيئات التطوير والاختبار والإنتاج.

---

## 1. متطلبات النظام

### 1.1 أنظمة التشغيل المدعومة

- Linux (موصى به): Ubuntu 20.04+ / Debian 11+
- macOS: 11 Big Sur أو أحدث
- Windows: يفضل استخدام WSL2 أثناء التطوير المحلي

### 1.2 الحد الأدنى من متطلبات الأجهزة

| المكون | الحد الأدنى | الموصى به | للإنتاج |
| --- | --- | --- | --- |
| المعالج | 4 أنوية | 8 أنوية | 16+ أنوية |
| الذاكرة | 8 جيجابايت | 16 جيجابايت | 32 جيجابايت+ |
| التخزين | 50 جيجابايت | 100 جيجابايت | 500 جيجابايت+ |
| GPU | اختياري | NVIDIA 8GB+ | NVIDIA 24GB+ |

### 1.3 البرامج المطلوبة

- Python 3.10+ (موصى به 3.11 أو 3.12)
- Git
- pip
- Docker (اختياري، موصى به للنشر بالحاويات)
- CUDA 11.8+ و cuDNN 8.6+ لدعم NVIDIA GPU (اختياري)

---

## 2. إعداد المشروع

### 2.1 استنساخ المشروع

```bash
git clone https://github.com/ahmedmokireldinonline/hermes-agent.git
cd hermes-agent
```

### 2.2 إنشاء بيئة افتراضية

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2.3 تثبيت التبعيات

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

إذا كان دعم الـ GPU مطلوباً:

```bash
pip install -r requirements-gpu.txt
```

لأدوات التطوير والاختبار:

```bash
pip install -r requirements-dev.txt
```

---

## 3. إعداد متغيرات البيئة

أنشئ ملفًا محليًا للبيئة:

```bash
cp .env.example .env
```

ثم عدّل الملف بالقيم المناسبة:

```env
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./hermes.db
OPENAI_API_KEY=your_key_here
HUGGING_FACE_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_key_here
USE_GPU=false
GPU_ID=0
LOG_LEVEL=INFO
LOG_FILE=logs/hermes.log
SECRET_KEY=your_secret_key
```

---

## 4. إعداد قاعدة البيانات

### SQLite (الافتراضي للتطوير المحلي)

```bash
python -m hermes.cli init-db
```

### PostgreSQL (موصى به للإنتاج)

```bash
# تثبيت PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# إنشاء المستخدم وقاعدة البيانات
createdb hermes_db
createuser hermes_user -P

# تحديث DATABASE_URL داخل .env
DATABASE_URL=postgresql://hermes_user:password@localhost:5432/hermes_db

# تشغيل الهجرات
alembic upgrade head
```

---

## 5. تشغيل التطبيق

### وضع التطوير

```bash
python -m uvicorn hermes.main:app --reload --host 0.0.0.0 --port 8000
```

### وضع الإنتاج

```bash
gunicorn hermes.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 6. إعداد Docker

### بناء الصورة

```bash
docker build -t hermes-agent:latest .
```

### تشغيل الحاوية

```bash
docker run -p 8000:8000 hermes-agent:latest
```

### مثال Docker Compose

```yaml
version: '3.9'

services:
  hermes:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./hermes.db
      - HUGGING_FACE_TOKEN=${HUGGING_FACE_TOKEN}
    restart: unless-stopped
```

---

## 7. الخدمات الخارجية

قد يتكامل Hermes Agent مع مزودين مختلفين:

| الخدمة | المتغير | ملاحظات |
| --- | --- | --- |
| Hugging Face | `HUGGING_FACE_TOKEN` | مطلوب لتنزيل النماذج ودمجها |
| OpenAI | `OPENAI_API_KEY` | اختياري |
| Anthropic | `ANTHROPIC_API_KEY` | اختياري |
| Google | `GOOGLE_API_KEY` | اختياري |

---

## 8. المراقبة والتسجيل

يجب كتابة السجلات في ملف ومن consola من أجل تصحيح الأخطاء في بيئة الإنتاج.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hermes.log'),
        logging.StreamHandler()
    ]
)
```

---

## 9. استكشاف الأخطاء

### أخطاء الاستيراد

```bash
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

### أخطاء قاعدة البيانات

```bash
python -m hermes.cli check-db
python -m hermes.cli reset-db --confirm
```

### عدم اكتشاف GPU

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### مشاكل المفاتيح API

افحص `HUGGING_FACE_TOKEN` و `OPENAI_API_KEY` وغيرها في ملف `.env` وتأكد أنها صحيحة.

---

## 10. أفضل ممارسات الأمان

- احتفظ بملف `.env` بعيداً عن نظام التحكم في الإصدارات.
- استخدم `SECRET_KEY` قويًا.
- قيد المنافذ العامة في بيئة الإنتاج.
- استخدم بروكسي عكسي مثل Nginx مع TLS.
- دوّر مفاتيح API بشكل دوري.

---

## 11. توصيات الأداء

- استخدم PostgreSQL للأحمال الإنتاجية.
- فعّل Redis للتخزين المؤقت إذا لزم الأمر.
- استخدم عمال متعددة في الإنتاج.
- استخدم GPU فقط لأعباء الاستدلال باستخدام النماذج الكبيرة.

---

## 12. الدعم

- مستودع GitHub: https://github.com/ahmedmokireldinonline/hermes-agent
- المشكلات: https://github.com/ahmedmokireldinonline/hermes-agent/issues

---

هذا المستند موجه كدليل عملي للنشر لـ Hermes Agent. اضبط الإعداد حسب بيئة النشر ومتطلبات النموذج الخاصة بك.
