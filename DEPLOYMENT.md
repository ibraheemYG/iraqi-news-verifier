# خطوات رفع المشروع على GitHub واستضافته

## 📤 الخطوة 1: رفع على GitHub

### 1. تهيئة Git (إذا لم يكن موجوداً)
```bash
cd C:\Users\brhm\Desktop\rag
git init
git add .
git commit -m "Initial commit: Iraqi News Verifier"
```

### 2. ربط بـ GitHub
```bash
# غيّر الرابط إلى رابط الريبو الخاص بك
git remote add origin https://github.com/ibraheemYG/iraqi-news-verifier.git
git branch -M main
git push -u origin main
```

---

## 🌐 الخطوة 2: النشر على الإنترنت

### الخيار 1: Streamlit Community Cloud (الأسهل) ⭐

#### المميزات:
- ✅ مجاني 100%
- ✅ نشر تلقائي من GitHub
- ✅ لا يتطلب بطاقة ائتمان
- ⚠️ محدود للواجهة فقط (Streamlit)

#### الخطوات:
1. اذهب إلى: https://share.streamlit.io
2. اضغط "New app"
3. اختر الريبو: `iraqi-news-verifier`
4. اختر الملف: `app.py`
5. أضف المتغيرات البيئية في "Advanced settings":
   ```
   GEMINI_API_KEY=your_key
   TELEGRAM_API_ID=your_id
   TELEGRAM_API_HASH=your_hash
   ```
6. اضغط "Deploy"

**ملاحظة**: ستحتاج لتشغيل API بشكل منفصل أو دمجه مع Streamlit.

---

### الخيار 2: Render (موصى به للمشروع الكامل) 🚀

#### المميزات:
- ✅ مجاني (750 ساعة/شهر)
- ✅ يدعم FastAPI + Streamlit
- ✅ قاعدة بيانات PostgreSQL مجانية
- ⚠️ يحتاج بطاقة ائتمان (لكن لن يحاسبك)

#### الخطوات:
1. اذهب إلى: https://render.com
2. سجّل دخول بحساب GitHub
3. اضغط "New" → "Web Service"
4. اختر الريبو: `iraqi-news-verifier`
5. املأ البيانات:
   ```
   Name: iraqi-news-verifier
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run app.py --server.port=$PORT
   ```
6. أضف المتغيرات البيئية
7. اضغط "Create Web Service"

---

### الخيار 3: Hugging Face Spaces (للمشاريع ML) 🤗

#### المميزات:
- ✅ مجاني
- ✅ دعم ممتاز لنماذج Transformers
- ✅ مساحة تخزين جيدة
- ⚠️ يحتاج تعديلات بسيطة

#### الخطوات:
1. اذهب إلى: https://huggingface.co/spaces
2. اضغط "Create new Space"
3. اختر "Streamlit"
4. ارفع الملفات أو اربط GitHub
5. أضف ملف `requirements.txt`
6. انتظر البناء التلقائي

---

## ⚙️ تعديلات مطلوبة للنشر

### 1. تعديل app.py لاستخدام API خارجي:
```python
# في app.py، غيّر:
API_URL = "http://127.0.0.1:8001/verify"

# إلى (بعد نشر API):
API_URL = "https://your-api.render.com/verify"
```

### 2. إضافة متغيرات البيئة:
في كل منصة، أضف:
```
GEMINI_API_KEY=your_actual_key
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_actual_hash
```

### 3. حل مشكلة الحجم (إذا واجهت):
إذا كان AraBERT كبيراً جداً، استخدم نموذج أصغر:
```python
# في vector_store.py، غيّر:
model_name = "asafaya/bert-base-arabic"
# إلى:
model_name = "aubmindlab/bert-mini-arabic"
```

---

## 🔧 استكشاف الأخطاء

### خطأ: "Slug size too large"
**الحل**: احذف vectors.db من Git وأعد بناءه على السيرفر:
```bash
git rm --cached vectors.db
echo "vectors.db" >> .gitignore
git commit -m "Remove large db file"
git push
```

### خطأ: "Out of memory"
**الحل**: استخدم نموذج أصغر أو قلل عدد المقالات المخزنة.

### خطأ: "Port already in use"
**الحل**: استخدم `$PORT` المتغير الذي توفره المنصة.

---

## 📊 مقارنة المنصات

| الميزة | Streamlit Cloud | Render | Hugging Face |
|--------|----------------|--------|--------------|
| السعر | مجاني | مجاني (محدود) | مجاني |
| سهولة النشر | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| دعم API | ❌ | ✅ | محدود |
| الأداء | متوسط | جيد | جيد |
| مساحة التخزين | محدودة | جيدة | ممتازة |

---

## 🎯 التوصية النهائية

**للمشروع الكامل (API + Frontend):**
استخدم **Render** - خدمتين منفصلتين:
1. Web Service للـ Streamlit
2. Web Service للـ FastAPI

**للواجهة فقط:**
استخدم **Streamlit Community Cloud** (أسهل وأسرع)

---

## 📞 الدعم

إذا واجهت مشاكل، تواصل عبر:
- GitHub Issues: https://github.com/ibraheemYG/iraqi-news-verifier/issues
- Email: your-email@example.com
