#!/usr/bin/env python
"""
اختبار سريع لحالة النظام
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from django.conf import settings
from surveys.models import Survey, Graduate
from graduates.models import Graduate as GradModel

def quick_system_test():
    """اختبار سريع لحالة النظام"""
    print("🔍 اختبار سريع لحالة النظام")
    print("=" * 50)
    
    # اختبار قاعدة البيانات
    print("📊 اختبار قاعدة البيانات:")
    try:
        survey_count = Survey.objects.count()
        graduate_count = Graduate.objects.count()
        grad_count = GradModel.objects.count()
        
        print(f"   عدد الاستبيانات: {survey_count}")
        print(f"   عدد الخريجين (surveys): {graduate_count}")
        print(f"   عدد الخريجين (graduates): {grad_count}")
        print("   ✅ قاعدة البيانات تعمل بشكل صحيح")
    except Exception as e:
        print(f"   ❌ خطأ في قاعدة البيانات: {str(e)}")
    
    # اختبار إعدادات البريد الإلكتروني
    print("\n📧 اختبار إعدادات البريد الإلكتروني:")
    print(f"   الخادم: {settings.EMAIL_HOST}")
    print(f"   المنفذ: {settings.EMAIL_PORT}")
    print(f"   المستخدم: {settings.EMAIL_HOST_USER}")
    print(f"   TLS مفعل: {settings.EMAIL_USE_TLS}")
    
    if settings.EMAIL_HOST_USER == 'your-email@gmail.com':
        print("   ⚠️  تحتاج تحديث إعدادات البريد الإلكتروني")
    else:
        print("   ✅ إعدادات البريد الإلكتروني محدثة")
    
    # اختبار الخريجين
    print("\n👥 اختبار الخريجين:")
    try:
        abofars = Graduate.objects.filter(email='abofars2022p@gmail.com').first()
        if abofars:
            print(f"   ✅ الخريج أبو فارس موجود: {abofars.full_name}")
        else:
            print("   ❌ الخريج أبو فارس غير موجود")
    except Exception as e:
        print(f"   ❌ خطأ في البحث عن الخريج: {str(e)}")
    
    # اختبار الاستبيانات
    print("\n📋 اختبار الاستبيانات:")
    try:
        surveys = Survey.objects.all()[:5]
        print(f"   عدد الاستبيانات: {Survey.objects.count()}")
        for i, survey in enumerate(surveys, 1):
            print(f"   {i}. {survey.title} (ID: {survey.id})")
    except Exception as e:
        print(f"   ❌ خطأ في الاستبيانات: {str(e)}")
    
    # اختبار الخادم
    print("\n🌐 اختبار الخادم:")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        if result == 0:
            print("   ✅ الخادم يعمل على المنفذ 8000")
        else:
            print("   ❌ الخادم غير متاح على المنفذ 8000")
        sock.close()
    except Exception as e:
        print(f"   ❌ خطأ في اختبار الخادم: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 انتهى الاختبار السريع")
    print("\n📋 ملاحظات:")
    print("   - إذا كانت إعدادات البريد غير محدثة، راجع SETUP_ABOFARS_EMAIL.md")
    print("   - إذا كان الخادم لا يعمل، شغّل: python manage.py runserver")
    print("   - للاختبار الكامل: python test_survey_to_abofars.py")

if __name__ == "__main__":
    quick_system_test() 