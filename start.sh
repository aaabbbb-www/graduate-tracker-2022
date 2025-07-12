#!/bin/bash

# نص تشغيل سريع لنظام تتبع الخريجين
# Quick Start Script for Graduate Tracker System

echo "🎓 مرحباً بك في نظام تتبع الخريجين"
echo "====================================="

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت. يرجى تثبيت Python 3.12 أو أحدث"
    exit 1
fi

# التحقق من وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip غير مثبت. يرجى تثبيت pip"
    exit 1
fi

echo "✅ Python و pip متوفران"

# إنشاء البيئة الافتراضية إذا لم تكن موجودة
if [ ! -d "venv" ]; then
    echo "📦 إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
echo "🔧 تفعيل البيئة الافتراضية..."
source venv/bin/activate

# تثبيت المتطلبات
echo "📥 تثبيت المتطلبات..."
pip install --upgrade pip
pip install -r requirements.txt

# إنشاء ملف .env إذا لم يكن موجوداً
if [ ! -f ".env" ]; then
    echo "⚙️ إنشاء ملف الإعدادات..."
    cp .env.example .env
    echo "📝 يرجى تحديث ملف .env بإعدادات قاعدة البيانات الخاصة بك"
fi

# التحقق من وجود قاعدة البيانات
echo "🗄️ التحقق من قاعدة البيانات..."

# إنشاء الهجرات
echo "📋 إنشاء هجرات قاعدة البيانات..."
python manage.py makemigrations accounts
python manage.py makemigrations graduates  
python manage.py makemigrations surveys
python manage.py makemigrations reports

# تطبيق الهجرات
echo "🔄 تطبيق الهجرات..."
python manage.py migrate

# جمع الملفات الثابتة
echo "📁 جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

# إنشاء مستخدم إداري إذا لم يكن موجوداً
echo "👤 إعداد المستخدم الإداري..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('تم إنشاء مستخدم إداري: admin/admin123')
else:
    print('المستخدم الإداري موجود مسبقاً')
"

echo ""
echo "🎉 تم إعداد النظام بنجاح!"
echo ""
echo "📋 معلومات مهمة:"
echo "   - رابط النظام: http://localhost:8000"
echo "   - لوحة الإدارة: http://localhost:8000/admin"
echo "   - اسم المستخدم: admin"
echo "   - كلمة المرور: admin123"
echo ""
echo "🚀 لتشغيل النظام:"
echo "   python manage.py runserver"
echo ""

# تشغيل الخادم
read -p "هل تريد تشغيل الخادم الآن؟ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 تشغيل الخادم..."
    python manage.py runserver
fi

