# مرجع API — Hermes Agent

## عنوان التشغيل

في التشغيل المحلي يكون العنوان:

```text
http://localhost:8000
```

في الإنتاج استخدم HTTPS وReverse Proxy ولا تعرض API مباشرة للإنترنت.

## المصادقة

أرسل المفتاح في كل endpoint محمي:

```http
X-API-Key: <your-api-key>
```

يتم رفض المفتاح غير الصحيح بـ`401`. في الإنتاج لا يسمح التطبيق بمفاتيح فارغة أو `change-me`.

## `GET /health`

فحص سريع لحالة التطبيق وقاعدة البيانات.

مثال استجابة:

```json
{
  "status": "ok",
  "database": "ok",
  "redis": "configured",
  "llm": "mock"
}
```

## `GET /ready`

فحص جاهزية الخدمة. يعيد `503` إذا كانت قاعدة البيانات غير جاهزة.

## `POST /tasks`

إنشاء مهمة جديدة.

### الطلب

```json
{
  "input": "Calculate the occupancy rate for 18 booked nights out of 30",
  "priority": "normal",
  "idempotency_key": "occupancy-001"
}
```

الحقول الإضافية مرفوضة. `input` مطلوب وطوله الأقصى 100,000 حرف. `priority` يقبل `low` أو `normal` أو `high`. مفتاح idempotency يقبل أحرفاً وأرقاماً وفواصل محددة وبحد أقصى 128 حرفاً.

### الاستجابة

يعيد endpoint حالة `202` مع المهمة. في الوضع inline قد تكون الحالة `succeeded` مباشرة، وفي وضع Redis تبدأ عادةً بـ`queued`.

```json
{
  "id": "uuid-v4",
  "input": "Calculate the occupancy rate for 18 booked nights out of 30",
  "status": "succeeded",
  "role": "reasoner",
  "result": "60%",
  "score": 8.2,
  "critique": "...",
  "reusable": false,
  "steps": [],
  "retries": 0,
  "failure_reason": null,
  "created_at": "2026-10-09T00:00:00Z",
  "updated_at": "2026-10-09T00:00:01Z"
}
```

## `GET /tasks/{task_id}`

قراءة مهمة يملكها نفس مفتاح API الذي أنشأها. إذا لم تكن المهمة موجودة أو لا يملكها المفتاح، يعيد endpoint `404` دون كشف معلومات إضافية.

## الأخطاء

| الحالة | المعنى |
|---:|---|
| `401` | مصادقة مفقودة أو غير صحيحة |
| `404` | المورد غير موجود أو ليس مملوكاً للمفتاح |
| `413` | الطلب أكبر من الحد المسموح |
| `422` | فشل التحقق من المدخلات |
| `429` | تجاوز معدل الطلبات؛ راجع `Retry-After` |
| `503` | الخدمة غير جاهزة |

## الإعدادات المرتبطة

`API_KEYS` للمصادقة، `RATE_LIMIT_PER_MIN` لمحدد المعدل، `MAX_TASK_SECONDS` و`MAX_STEPS` للحدود، `QUEUE_MODE` لاختيار inline أو Redis، و`OLLAMA_URL` لبوابة النموذج. راجع `.env.example` و`README.md` قبل النشر.
