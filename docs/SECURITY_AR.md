# وثيقة الأمان — Hermes Agent

**المالك:** Ahmed MO Kireldin  
**الموقع:** https://Ahmedmokireldin.online

## الهدف

تشرح هذه الوثيقة الحدود الأمنية والضوابط الحالية في Hermes Agent، وهو نظام متعدد الوكلاء يعمل محلياً أو داخل Docker مع FastAPI وRedis وSQLAlchemy وOllama.

## ضوابط أساسية

### المصادقة والملكية

في بيئة الإنتاج يجب ضبط `ENV=prod` و`API_KEYS` بقيم عشوائية طويلة. يرفض التطبيق التشغيل إذا كانت المفاتيح فارغة أو تساوي `change-me`. تتم مقارنة المفاتيح باستخدام `hmac.compare_digest`، وتُربط كل مهمة بمالكها حتى لا يستطيع مفتاح قراءة مهام مالك آخر.

### حدود الطلبات

تستخدم طبقة Pydantic التحقق من طول الإدخال و`idempotency_key` والحقول غير المعروفة. يوجد حد لحجم الطلب ومحدد معدل لكل مفتاح API، ويعاد الخطأ `429` مع `Retry-After` عند تجاوزه.

### الأدوات وSSRF

تعمل أدوات الملفات داخل `workspace/` فقط، وترفض المسارات المطلقة و`..` وفواصل Windows والـnull bytes والروابط الرمزية. يفرض مشغل Python مهلة وحدود CPU والذاكرة والعمليات وحجم الملف، لكنه **ليس Sandbox قوياً**.

تتحقق أداة HTTP من البروتوكول والمنفذ والعنوان العام، وترفض localhost وmetadata endpoints والعناوين الخاصة والـloopback والـlink-local والـmulticast والعناوين المحجوزة، وتعطل التحويلات وتمنع بيانات الاعتماد في الرابط. يجب إضافة اختبار DNS rebinding وtransport مثبت العنوان قبل الإنتاج عالي الحساسية.

الـWebhook لا يعمل إلا عبر Allowlist دقيقة، ويطبق العامل الضابط نفسه الموجود في API. لا تضف endpoint إلى `WEBHOOK_ALLOW` إلا بعد مراجعته.

### المهارات الخارجية وحقن التعليمات

تُحفظ المهارة المستوردة كـcandidate غير موثوق. يتم التحقق من HTTPS واسم المضيف وحجم التنزيل أثناء البث وContent-Type وSHA-256. مصادر GitHub/GitLab تحتاج commit SHA مثبتاً. لا تُحقن المهارة في prompts ولا تحصل على صلاحيات حتى ينفذ مسؤول صريح:

```bash
python scripts/approve_skill.py skills/candidates/name-hash.md --approver owner
```

المحتوى الخارجي ومخرجات النماذج بيانات وليست تعليمات نظام، وتستخدم prompts فواصل واضحة لهذه البيانات.

### Docker

تستخدم الحاويات مستخدم non-root، وfilesystem للقراءة فقط، و`tmpfs` للملفات المؤقتة، وتسقط capabilities، وتستخدم `no-new-privileges` وحدود CPU والذاكرة والعمليات. لا يتم نشر PostgreSQL أو Redis على الجهاز المضيف، ويُطلب password من `.env` مع healthchecks وRedis authentication.

## الأسرار والبيانات

لا تضع الأسرار داخل prompts أو traces أو commits. يبقى `.env` خارج Git. يجب إضافة redaction كامل لمفاتيح API والرموز والبريد والهواتف قبل تخزين traces في بيئة الإنتاج.

## قائمة تشغيل آمن

1. اضبط الأسرار عبر Secret Manager.
2. شغل `alembic upgrade head` قبل API وWorker.
3. ضع Reverse Proxy وTLS ومحدد معدل خارجي.
4. فعّل sandbox لكل كود غير موثوق.
5. اختبر استعادة قاعدة البيانات وإعادة المهام بعد توقف العامل.
6. راجع تراخيص النماذج والمهارات قبل الاستخدام التجاري.
