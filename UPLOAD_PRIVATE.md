# 🔒 رفع المشروع على GitHub كـ Private

## ✅ ما تم إنجازه:
- [x] Git initialized
- [x] الملفات تمت إضافتها
- [x] Commit تم بنجاح

---

## 📝 الخطوات المتبقية (5 دقائق):

### **الخطوة 1: إنشاء Repository على GitHub (Private)**

1. افتح: https://github.com/new

2. املأ البيانات:
   ```
   Repository name: iraqi-news-verifier
   Description: نظام ذكي للتحقق من الأخبار العراقية - مشروع ماجستير
   
   ⚠️ مهم جداً: اختر "Private" 🔒
   
   □ لا تضف README
   □ لا تضف .gitignore
   □ لا تضف License
   ```

3. اضغط **"Create repository"**

---

### **الخطوة 2: ربط المشروع بـ GitHub**

بعد إنشاء الـ repo، انسخ الأوامر من GitHub وشغّلها:

```powershell
# في PowerShell (نفس النافذة):

# تغيير اسم الـ branch
git branch -M main

# ربط بالـ repo (غيّر الرابط من GitHub!)
git remote add origin https://github.com/ibraheemYG/iraqi-news-verifier.git

# رفع الملفات
git push -u origin main
```

**ملاحظة**: ستطلب منك GitHub:
- Username: ibraheemYG
- Password: استخدم **Personal Access Token** (ليس كلمة المرور!)

---

### **الخطوة 3: إنشاء Personal Access Token (إذا لزم)**

إذا طلب منك كلمة مرور:

1. اذهب: https://github.com/settings/tokens
2. اضغط **"Generate new token (classic)"**
3. املأ:
   ```
   Note: Iraqi News Verifier
   Expiration: 90 days
   Scopes: ✅ repo (فقط)
   ```
4. اضغط **Generate token**
5. **انسخ الـ token فوراً** (لن تراه مرة أخرى!)
6. استخدمه بدل كلمة المرور

---

## 🌐 الخطوة 4: نشر الواجهة (عامة للمستخدمين)

### **الطريقة الموصى بها: Streamlit Community Cloud**

1. اذهب: https://share.streamlit.io

2. اضغط **"New app"**

3. املأ البيانات:
   ```
   Repository: ibraheemYG/iraqi-news-verifier
   Branch: main
   Main file path: app.py
   ```

4. اضغط **"Advanced settings"**

5. أضف Secrets (المفاتيح الحساسة):
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   TELEGRAM_API_ID = "12345678"
   TELEGRAM_API_HASH = "your_actual_hash_here"
   ```

6. اضغط **"Deploy!"**

⏱️ الانتظار: 5-10 دقائق

---

## ✅ النتيجة النهائية:

### **الكود (Private 🔒):**
```
https://github.com/ibraheemYG/iraqi-news-verifier
👁️ يراه: أنت فقط
```

### **الواجهة (Public 🌐):**
```
https://your-app-name.streamlit.app
👁️ يراه: الجميع (لكن بدون الكود!)
```

---

## 🔐 الأمان:

✅ **محمي:**
- الكود على GitHub Private
- المفاتيح في Streamlit Secrets
- vectors.db لن يُرفع (في .gitignore)

❌ **غير محمي:**
- الواجهة متاحة للجميع (مطلوب)
- لكن لا أحد يستطيع رؤية الكود!

---

## 🛠️ إذا واجهت مشكلة:

### **خطأ: Authentication failed**
**الحل**: استخدم Personal Access Token بدل كلمة المرور

### **خطأ: Repository not found**
**الحل**: تأكد أن الـ repo على GitHub أصبح Private

### **خطأ: Streamlit can't access private repo**
**الحل**: 
1. اذهب لإعدادات الـ repo
2. Settings → Integrations → Streamlit
3. أعط الإذن

---

## 📞 الدعم:

إذا واجهت مشاكل، ارسل screenshot من الخطأ.

---

**جاهز؟ ابدأ من الخطوة 1!** 🚀
