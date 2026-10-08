# Hermes Agent MVP

**Project owner:** Ahmed MO Kireldin  
**Website:** [Ahmedmokireldin.online](https://Ahmedmokireldin.online)

## 📞 Official contact

- Phone: `+201012025650`
- Phone: `+201006334062`
- Email: [Ahmedmokireldin.online@gmail.com](mailto:Ahmedmokireldin.online@gmail.com)

These contact details identify the project owner and are included at the owner's request.

نسخة MVP قابلة للتشغيل من منصة Hermes Agent متعددة الوكلاء. تنفذ المسار الأساسي: استقبال المهمة، التوجيه، تنفيذ النموذج، التقييم، والحفظ. تدعم التشغيل المحلي في وضع Mock وتشغيل Redis/Postgres عبر Docker Compose، كما تتضمن Profiles لنماذج مفتوحة الأوزان قابلة للتشغيل محلياً.

> Hermes Agent is an independent self-hosted project owned by **Ahmed MO Kireldin**. Third-party model weights, names, trademarks, and licenses remain with their respective owners.

> هذه النسخة MVP وليست جاهزة لتعريضها للإنترنت دون reverse proxy وTLS وrate limiting وSSRF hardening وsandbox أقوى.

## المكونات

- FastAPI: `POST /tasks`, `GET /tasks/{id}`, `GET /health`
- SQLAlchemy async: SQLite محلياً أو PostgreSQL عبر Docker
- Redis queue: اختياري محلياً، ومفعّل في Compose
- Router / Executor / Critic: Mock افتراضياً أو Ollama
- أدوات مقيدة: workspace files، Python timeout، HTTP public-only، webhook allowlist
- Worker مستقل عند `QUEUE_MODE=redis`
- Profiles للنماذج: `lite`, `balanced`, `quality`
- تسلسل وكلاء داخلي موثق مع عقود handoff وقيود صلاحيات

## تشغيل سريع محلياً

```bash
cd hermes-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api:app --reload --port 8000
```

في الوضع المحلي الافتراضي تكون المهام Inline و`MOCK_LLM=true`، لذلك لا تحتاج إلى Ollama أو Redis.

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"input":"احسب نسبة الإشغال لـ 18 ليلة من أصل 30"}'
```

إذا عيّنت `API_KEYS`، أرسل `X-API-Key` مع الطلبات.

## التشغيل عبر Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

ثم أرسل المهمة:

```bash
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"input":"Draft a customer update about this week\'s bookings", "idempotency_key":"booking-001"}'
```

يعيد API مهمة بحالة `queued`. نفّذ `GET /tasks/{id}` حتى تصبح `succeeded`.

## 🧠 Open Model Fleet

يوجد ملف `config/models.open.yaml` بتشكيلات مبدئية:

| Profile | الاستخدام | النماذج الرئيسية |
|---|---|---|
| `lite` | جهاز واحد أو ذاكرة محدودة | Qwen3 4B/8B، Qwen Coder 7B، Granite 8B |
| `balanced` | خادم GPU متوسط | Qwen3 14B، DeepSeek-R1 Distill 14B، Mistral Small 3.1 24B |
| `quality` | GPU قوي أو عدة خوادم | Qwen3 32B، DeepSeek-R1 Distill 32B، Qwen Coder 32B |

اسحب النماذج المحددة عبر Ollama:

```bash
PROFILE=lite ./scripts-pull-models.sh
```

راجع التراخيص قبل الاستخدام التجاري أو إعادة التوزيع؛ Open Weights لا تعني دائماً OSI Open Source. التوثيق الكامل موجود في [docs-open-models.md](docs-open-models.md)، مع [OWNER.md](OWNER.md) و[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### التسلسل الداخلي المقترح

`👤 User → 🔐 API → ⚡ Router → 🧭 Planner → 📚 Skills → 🧩 Specialist → 🛠️ Tools → 🔎 Critic → 🗄️ Trace → 🔄 Evolver`

## تشغيل Ollama

1. شغّل Ollama خارج Compose أو أضف خدمة Ollama إلى بيئتك.
2. اسحب Profile مناسباً عبر `scripts-pull-models.sh`.
3. اضبط `MOCK_LLM=false` و`OLLAMA_URL`.
4. راجع `config/models.open.yaml` قبل التشغيل.

## هيكل المشروع

```text
app/
  api.py       FastAPI endpoints
  agent.py     route → execute → critic
  db.py        SQLAlchemy models
  llm.py       Mock/Ollama gateway with model profiles
  queue.py     Redis queue adapter
  worker.py    queue worker
  tools.py     constrained tools
  evolver.py   conservative self-improvement entry point
config/        model roles and open-weight profiles
prompts/       role guidance
tests/         automated and regression tests
workspace/     confined file workspace
docs-open-models.md  model fleet and agent handoff
docs-architecture.md architecture diagrams
docs/index.html      responsive project landing page with inline icons
```

## 🧰 External Skills من GitHub والمنصات الأخرى

يمكن استيراد Skill خارجية كمرشح غير موثوق من GitHub أو GitLab أو Hugging Face:

```bash
python scripts/import_skill.py \
  https://raw.githubusercontent.com/OWNER/REPO/main/SKILL.md \
  --name booking-followup
```

تُحفظ المهارة في `skills/candidates/` بعد فحص HTTPS وAllowlist وحساب Content Hash. لا تُعتمد ولا تُمنح صلاحيات أدوات تلقائياً؛ راجع [docs-skills.md](docs-skills.md).

## حالة MVP وما لم يُنفذ بعد

النسخة الحالية توفر المسار الأساسي، لكنها لا تتضمن بعد: pgvector retrieval حقيقياً، reranker، audio/vision services، Evolver كامل، migrations Alembic، distributed leases، full rate limiting، human approval UI، metrics export، أو Firecracker isolation. أضف هذه المكونات بعد تثبيت الاستخدام وكتابة اختبارات التكامل.

## معايير الأمان

- لا تضع الأسرار داخل prompts أو traces.
- لا تفتح API للعامة مباشرة.
- ضع reverse proxy وTLS وrate limiting.
- أبقِ `WEBHOOK_ALLOW` فارغاً حتى تضيف endpoints مقصودة.
- اعتبر كل محتوى HTTP بيانات غير موثوقة.
- استخدم sandbox أقوى من subprocess لتشغيل كود غير موثوق.
- راجع الترخيص الدقيق لكل نموذج قبل الاستخدام التجاري.
