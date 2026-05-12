# 🔍 متحقق الأخبار العراقي | Iraqi News Verifier# مُتحقق الأخبار العراقي - Iraqi News Verifier



نظام ذكي للتحقق من الأخبار باستخدام تقنية RAG (الاسترجاع المعزز بالتوليد) ونموذج AraBERT.نظام ذكي للتحقق من صحة الأخبار العراقية باستخدام قاعدة بيانات من القنوات الموثوقة في تليجرام.



## ✨ الميزات## الملفات الأساسية



- 🤖 **تحقق ذكي**: يستخدم AraBERT لفهم النصوص العربية### الملفات الرئيسية:

- 📊 **قاعدة بيانات موثوقة**: يجمع الأخبار من قنوات تليجرام ومواقع حكومية عراقية- `api.py` - خادم FastAPI الرئيسي

- 🔄 **تحديثات تلقائية**: يجلب آخر الأخبار من المصادر الموثوقة- `app.py` - واجهة Streamlit للمستخدمين

- 💬 **إجابة أسئلة**: يمكنه الإجابة على أسئلة بناءً على قاعدة المعرفة- `simple_db.py` - إدارة قاعدة البيانات (SQLite)

- 🎯 **فهم المرادفات**: يتعرف على الأسماء المختصرة والمرادفات- `simple_rag.py` - نظام الاسترجاع والتوليد

- `telegram_reader.py` - قارئ منشورات تليجرام

## 🛠️ التقنيات المستخدمة- `telegram_login.py` - إعداد تسجيل دخول تليجرام

- `config.py` - إعدادات التطبيق والقنوات الموثوقة

- **Backend**: FastAPI + Uvicorn

- **Frontend**: Streamlit### ملفات البيانات:

- **AI/ML**: - `simple_news.db` - قاعدة بيانات الأخبار

  - AraBERT (`asafaya/bert-base-arabic`)- `telegram_sessions/` - ملفات جلسات تليجرام

  - Google Gemini (مع Ollama كبديل)

- **Database**: SQLite + Vector Store## متطلبات التشغيل

- **Data Sources**: Telegram API + Web Scraping

1. تثبيت المكتبات المطلوبة:

## 📦 التثبيت```bash

pip install -r requirements.txt

### المتطلبات```

- Python 3.10+

- حساب Telegram (للحصول على الأخبار)2. تثبيت وتشغيل Ollama مع النموذج المطلوب:

- مفتاح Gemini API (اختياري)```bash

ollama pull gpt-oss:120b-cloud

### الخطوات```



```bash3. إعداد Telegram API:

# 1. استنساخ المشروع   - احصل على API_ID و API_HASH من https://my.telegram.org

git clone https://github.com/ibraheemYG/social-graph-collector.git   - قم بتحديث `config.py` بالبيانات الصحيحة

cd social-graph-collector

## طريقة التشغيل

# 2. إنشاء البيئة الافتراضية

python -m venv .venv1. تشغيل خادم API:

```bash

# Windows:python api.py

.venv\Scripts\activate```



# Linux/Mac:2. تشغيل واجهة المستخدم (في نافذة طرفية أخرى):

# source .venv/bin/activate```bash

streamlit run app.py

# 3. تثبيت المكتبات```

pip install -r requirements.txt

3. الوصول للتطبيق عبر المتصفح:

# 4. إعداد ملف البيئة (اختياري)   - واجهة المستخدم: http://localhost:8501

# أنشئ ملف .env وأضف:   - API Documentation: http://127.0.0.1:8000/docs

# GEMINI_API_KEY=your_key_here

# TELEGRAM_API_ID=your_api_id## المميزات

# TELEGRAM_API_HASH=your_api_hash

```- ✅ واجهة سهلة الاستخدام باللغة العربية

- ✅ تحقق سريع من الأخبار باستخدام AI

## 🚀 التشغيل- ✅ جلب تلقائي من قنوات تليجرام الموثوقة

- ✅ قاعدة بيانات بسيطة وسريعة

```bash- ✅ نظام تسجيل للأخبار غير المؤكدة

# 1. تشغيل الخادم الخلفي (API)

python -m uvicorn api:app --host 127.0.0.1 --port 8001## القنوات الموثوقة المدعومة



# 2. في نافذة أخرى، شغّل الواجهةانظر ملف `config.py` لقائمة القنوات الموثوقة المستخدمة في النظام.

streamlit run app.py

```## الاستخدام



ثم افتح المتصفح على: `http://localhost:8501`1. ادخل النص المراد التحقق منه

2. اضغط "تحقق الآن"

## 📚 البنية3. احصل على النتيجة: موثوق أو غير مؤكد

4. استخدم Admin Panel لتحديث قاعدة البيانات من تليجرام
```
rag/
├── api.py              # FastAPI backend
├── app.py              # Streamlit frontend  
├── config.py           # القنوات الموثوقة والإعدادات
├── vector_store.py     # قاعدة البيانات المتجهة
├── rag_arabert.py      # نموذج الذكاء الاصطناعي
├── telegram_reader.py  # قراءة التليجرام
├── news_fetchers.py    # جلب الأخبار من المواقع
├── requirements.txt    # المكتبات
└── .gitignore          # ملفات مستثناة من Git
```

## 🌐 النشر على الإنترنت

### خيارات الاستضافة المجانية:

1. **Streamlit Community Cloud** (الأسهل)
   - مجاني تماماً
   - نشر مباشر من GitHub
   - محدود لتطبيقات Streamlit فقط

2. **Render** (موصى به)
   - مجاني
   - يدعم FastAPI + Streamlit
   - 750 ساعة مجانية/شهر

3. **Railway**
   - مجاني للبداية
   - سهل التكوين
   - $5 رصيد مجاني

4. **Hugging Face Spaces**
   - مجاني
   - مناسب لمشاريع ML
   - دعم جيد لنماذج Transformers

## 🎓 مشروع ماجستير

هذا المشروع جزء من بحث الماجستير في **التحقق من الأخبار باستخدام تقنيات الذكاء الاصطناعي**.

## ⚠️ ملاحظات

- النظام يعتمد على مصادر عراقية محلية
- الدقة تعتمد على جودة البيانات في قاعدة المعرفة
- يُوصى بتحديث البيانات بشكل دوري
- حجم نموذج AraBERT: ~500 MB

## 📝 المتغيرات البيئية

قم بإنشاء ملف `.env` في المجلد الرئيسي:

```env
# Google Gemini (اختياري)
GEMINI_API_KEY=your_gemini_api_key_here

# Telegram API (مطلوب لجلب الأخبار)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+964xxxxxxxxxx

# Ollama (بديل محلي)
OLLAMA_MODEL=deepseek-v3.1:671b-cloud
```

## 📄 الترخيص

MIT License

## 👨‍💻 المطور

إبراهيم ياسين - مشروع بحث الماجستير
