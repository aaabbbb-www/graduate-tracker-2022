@echo off
chcp 65001 >nul
echo 🎓 مرحباً بك في نظام تتبع الخريجين
echo =====================================

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت. يرجى تثبيت Python 3.12 أو أحدث
    pause
    exit /b 1
)

echo ✅ Python متوفر

REM إنشاء البيئة الافتراضية إذا لم تكن موجودة
if not exist "venv" (
    echo 📦 إنشاء البيئة الافتراضية...
    python -m venv venv
)

REM تفعيل البيئة الافتراضية
echo 🔧 تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat

REM تثبيت المتطلبات
echo 📥 تثبيت المتطلبات...
python -m pip install --upgrade pip



REM إنشاء ملف .env إذا لم يكن موجوداً
if not exist ".env" (
    echo ⚙️ إنشاء ملف الإعدادات...
    copy .env.example .env
    echo 📝 يرجى تحديث ملف .env بإعدادات قاعدة البيانات الخاصة بك
)

REM إنشاء الهجرات
echo 📋 إنشاء هجرات قاعدة البيانات...
python manage.py makemigrations accounts
python manage.py makemigrations graduates
python manage.py makemigrations surveys
python manage.py makemigrations reports

REM تطبيق الهجرات
echo 🔄 تطبيق الهجرات...
python manage.py migrate

REM جمع الملفات الثابتة
echo 📁 جمع الملفات الثابتة...
python manage.py collectstatic --noinput

REM إنشاء مستخدم إداري
echo 👤 إعداد المستخدم الإداري...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

echo.
echo 🎉 تم إعداد النظام بنجاح!
echo.
echo 📋 معلومات مهمة:
echo    - رابط النظام: http://localhost:8000
echo    - لوحة الإدارة: http://localhost:8000/admin
echo    - اسم المستخدم: admin
echo    - كلمة المرور: admin123
echo.
echo 🚀 لتشغيل النظام:
echo    python manage.py runserver
echo.

set /p choice="هل تريد تشغيل الخادم الآن؟ (y/n): "
if /i "%choice%"=="y" (
    echo 🚀 تشغيل الخادم...
    python manage.py runserver
)

pause

