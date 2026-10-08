# المعمارية — Hermes Agent

## نظرة عامة

Hermes Agent منصة محلية متعددة الوكلاء تستقبل المهمة من FastAPI، تحفظها في قاعدة البيانات، ثم تنفذها inline أو عبر Redis Worker. يختار Router الدور المناسب، ويعمل Specialist على المهمة، ثم يراجع Critic النتيجة قبل حفظ الحالة والتتبع.

```mermaid
flowchart TB
  USER[المستخدم] --> API[FastAPI API]
  API --> AUTH[مصادقة + Rate Limit]
  AUTH --> DB[(PostgreSQL / SQLite)]
  AUTH --> Q[(Redis Queue)]
  Q --> W[Worker]
  W --> R[Router]
  R --> S[استرجاع المهارات]
  S --> E[Executor Specialist]
  E --> P[Tool Policy + Sandbox]
  E --> C[Critic Schema]
  C --> DB
  E --> L[Ollama Gateway]
  EV[Evolver Proposal Only] --> RV[Review Directory]
```

## المكونات

| المكون | المسؤولية |
|---|---|
| FastAPI | المصادقة والتحقق وإنشاء المهام وقراءة المهام المملوكة |
| SQLAlchemy | حفظ المهام والتتبعات والتواريخ والفهارس |
| Redis | طابور المهام وprocessing list وACK |
| Worker | تنفيذ المهام بمهلة وإعادة محاولة وحد أقصى |
| Router | تحديد الدور المتخصص |
| Executor | تشغيل النموذج مع prompt boundaries |
| Tools | ملفات workspace وPython وHTTP وWebhook بضوابط |
| Critic | تحليل منظم عبر Pydantic |
| Evolver | إنشاء proposal فقط داخل `review/` |

## دورة المهمة

```mermaid
sequenceDiagram
  participant U as User
  participant A as API
  participant D as Database
  participant Q as Redis
  participant W as Worker
  participant M as Model
  U->>A: POST /tasks
  A->>A: Authenticate, validate, rate limit
  A->>D: Persist owner-scoped task
  A->>Q: Enqueue when queue mode is redis
  Q->>W: Claim into processing list
  W->>M: Route and execute within budgets
  M-->>W: Result and critic JSON
  W->>D: Persist result or failure
  W->>Q: ACK or retry
```

## تنظيم المسؤوليات

```mermaid
flowchart LR
  OWNER[مالك المشروع] --> SEC[Security + Policy]
  OWNER --> OPS[Operations + Deployments]
  OWNER --> AI[Models + Evaluation]
  SEC --> REVIEW[Skill Review + Approvals]
  OPS --> CI[CI + Backups + Monitoring]
  AI --> TESTS[Dev + Holdout + Regression]
```

## حدود الثقة

محتوى المستخدم والويب والمهارات ومخرجات النماذج غير موثوق. طبقة Policy هي الوحيدة التي تمنح الأدوات، ومالك المهمة هو الوحيد الذي يستطيع قراءة نتيجتها عبر API key نفسه. لا تعد هذه النسخة Sandbox قوياً لتشغيل كود عدائي.

## نقاط التطوير التالية

أضف visibility timeout وreaper للطابور، redaction قبل traces، metrics وOpenTelemetry، pgvector وreranker، sandbox لكل مهمة، وواجهة موافقة بشرية قبل الأفعال الخارجية غير القابلة للعكس.
