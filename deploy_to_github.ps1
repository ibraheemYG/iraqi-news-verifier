# سكريبت رفع المشروع على GitHub
# استخدم هذا بعد إنشاء ريبو جديد على GitHub

# 1. تهيئة Git
Write-Host "🔧 تهيئة Git..." -ForegroundColor Cyan
git init

# 2. إضافة جميع الملفات
Write-Host "📦 إضافة الملفات..." -ForegroundColor Cyan
git add .

# 3. الـ commit الأول
Write-Host "💾 Commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Iraqi News Verifier with RAG + AraBERT"

# 4. إنشاء branch main
Write-Host "🌿 إنشاء branch main..." -ForegroundColor Cyan
git branch -M main

# 5. ربط بـ GitHub (غيّر الرابط!)
Write-Host "🔗 ربط بـ GitHub..." -ForegroundColor Yellow
Write-Host "⚠️  غيّر الرابط في السطر التالي إلى رابط الريبو الخاص بك!" -ForegroundColor Red
# git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

Read-Host "اضغط Enter بعد تعديل الرابط في الملف..."

# 6. رفع على GitHub
Write-Host "🚀 رفع على GitHub..." -ForegroundColor Green
# git push -u origin main

Write-Host "✅ تم! المشروع الآن على GitHub" -ForegroundColor Green
Write-Host ""
Write-Host "الخطوات التالية:" -ForegroundColor Cyan
Write-Host "1. افتح GitHub.com واذهب للريبو" -ForegroundColor White
Write-Host "2. تأكد من رفع جميع الملفات" -ForegroundColor White  
Write-Host "3. اقرأ ملف DEPLOYMENT.md لخطوات النشر" -ForegroundColor White
