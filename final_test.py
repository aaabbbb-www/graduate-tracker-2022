#!/usr/bin/env python
"""
اختبار نهائي شامل لنظام تتبع الخريجين
"""
import os
import sys
import django
from datetime import datetime

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from surveys.models import Survey, Graduate
from surveys.whatsapp_service import EmailService

def final_comprehensive_test():
    """اختبار نهائي شامل"""
    print("🎯 اختبار نهائي شامل لنظام تتبع الخريجين")
    print("=" * 60)
    
    # 1. اختبار قاعدة البيانات
    print("\n📊 1. اختبار قاعدة البيانات:")
    try:
        survey_count = Survey.objects.count()
        graduate_count = Graduate.objects.count()
        print(f"   ✅ عدد الاستبيانات: {survey_count}")
        print(f"   ✅ عدد الخريجين: {graduate_count}")
    except Exception as e:
        print(f"   ❌ خطأ في قاعدة البيانات: {str(e)}")
    
    # 2. اختبار إعدادات البريد الإلكتروني
    print("\n📧 2. اختبار إعدادات البريد الإلكتروني:")
    print(f"   الخادم: {settings.EMAIL_HOST}")
    print(f"   المنفذ: {settings.EMAIL_PORT}")
    print(f"   المستخدم: {settings.EMAIL_HOST_USER}")
    print(f"   TLS مفعل: {settings.EMAIL_USE_TLS}")
    
    if settings.EMAIL_HOST_USER == 'your-email@gmail.com':
        print("   ⚠️  تحتاج تحديث إعدادات البريد الإلكتروني")
        print("   📝 راجع ملف SETUP_ABOFARS_EMAIL.md")
    else:
        print("   ✅ إعدادات البريد الإلكتروني محدثة")
    
    # 3. اختبار الخريجين
    print("\n👥 3. اختبار الخريجين:")
    try:
        abofars = Graduate.objects.filter(email='abofars2022p@gmail.com').first()
        if abofars:
            print(f"   ✅ الخريج أبو فارس موجود: {abofars.full_name}")
            print(f"   📧 البريد الإلكتروني: {abofars.email}")
            print(f"   📱 الهاتف: {abofars.phone}")
            print(f"   🎓 التخصص: {abofars.major}")
        else:
            print("   ❌ الخريج أبو فارس غير موجود")
    except Exception as e:
        print(f"   ❌ خطأ في البحث عن الخريج: {str(e)}")
    
    # 4. اختبار الاستبيانات
    print("\n📋 4. اختبار الاستبيانات:")
    try:
        surveys = Survey.objects.all()[:3]
        print(f"   عدد الاستبيانات: {Survey.objects.count()}")
        for i, survey in enumerate(surveys, 1):
            print(f"   {i}. {survey.title}")
            print(f"      - الحالة: {survey.status}")
            print(f"      - طريقة الإرسال: {survey.send_method}")
            print(f"      - عدد الأسئلة: {survey.questions.count()}")
    except Exception as e:
        print(f"   ❌ خطأ في الاستبيانات: {str(e)}")
    
    # 5. اختبار إرسال البريد الإلكتروني
    print("\n📤 5. اختبار إرسال البريد الإلكتروني:")
    try:
        # رسالة تجريبية
        subject = f"اختبار نهائي - نظام تتبع الخريجين - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        message = f"""
مرحباً،

هذا اختبار نهائي لنظام تتبع الخريجين.

تفاصيل الاختبار:
- التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- النظام: نظام تتبع الخريجين
- الحالة: اختبار نهائي شامل

إذا وصلت هذه الرسالة، فهذا يعني أن النظام يعمل بشكل صحيح.

شكراً لك!

فريق تطوير نظام تتبع الخريجين
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['abofars2022p@gmail.com']
        
        print(f"   📧 من: {from_email}")
        print(f"   📧 إلى: {recipient_list[0]}")
        print(f"   📧 الموضوع: {subject}")
        
        # محاولة الإرسال
        result = send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        if result == 1:
            print("   ✅ تم إرسال البريد الإلكتروني بنجاح!")
            print(f"   📊 عدد الرسائل المرسلة: {result}")
        else:
            print("   ❌ فشل في إرسال البريد الإلكتروني")
            print(f"   📊 عدد الرسائل المرسلة: {result}")
            
    except Exception as e:
        print(f"   ❌ خطأ في إرسال البريد الإلكتروني: {str(e)}")
        print("   🔧 تأكد من إعدادات Gmail في settings.py")
    
    # 6. اختبار الخادم
    print("\n🌐 6. اختبار الخادم:")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        if result == 0:
            print("   ✅ الخادم يعمل على المنفذ 8000")
            print("   🌐 يمكنك الوصول للنظام عبر: http://127.0.0.1:8000")
        else:
            print("   ❌ الخادم غير متاح على المنفذ 8000")
            print("   🔧 شغّل: python manage.py runserver")
        sock.close()
    except Exception as e:
        print(f"   ❌ خطأ في اختبار الخادم: {str(e)}")
    
    # 7. ملخص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج:")
    print("=" * 60)
    
    # حساب النقاط
    points = 0
    total_points = 6
    
    if Survey.objects.count() > 0:
        points += 1
        print("✅ قاعدة البيانات: تعمل بشكل صحيح")
    else:
        print("❌ قاعدة البيانات: تحتاج فحص")
    
    if settings.EMAIL_HOST_USER != 'your-email@gmail.com':
        points += 1
        print("✅ إعدادات البريد الإلكتروني: محدثة")
    else:
        print("❌ إعدادات البريد الإلكتروني: تحتاج تحديث")
    
    if Graduate.objects.filter(email='abofars2022p@gmail.com').exists():
        points += 1
        print("✅ الخريجين: موجودون")
    else:
        print("❌ الخريجين: يحتاجون إنشاء")
    
    if Survey.objects.count() > 0:
        points += 1
        print("✅ الاستبيانات: موجودة")
    else:
        print("❌ الاستبيانات: تحتاج إنشاء")
    
    # اختبار البريد الإلكتروني
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        if result == 0:
            points += 1
            print("✅ الخادم: يعمل")
        else:
            print("❌ الخادم: لا يعمل")
        sock.close()
    except:
        print("❌ الخادم: خطأ في الاختبار")
    
    # تقييم عام
    percentage = (points / total_points) * 100
    print(f"\n📈 التقييم العام: {points}/{total_points} ({percentage:.1f}%)")
    
    if percentage >= 80:
        print("🎉 ممتاز! النظام يعمل بشكل جيد")
    elif percentage >= 60:
        print("👍 جيد! النظام يعمل بشكل مقبول")
    elif percentage >= 40:
        print("⚠️  مقبول! يحتاج بعض التحسينات")
    else:
        print("❌ يحتاج إصلاحات عديدة")
    
    print("\n📋 التوصيات:")
    if settings.EMAIL_HOST_USER == 'your-email@gmail.com':
        print("   1. تحديث إعدادات البريد الإلكتروني في settings.py")
    if not Graduate.objects.filter(email='abofars2022p@gmail.com').exists():
        print("   2. إنشاء الخريج أبو فارس")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        if result != 0:
            print("   3. تشغيل الخادم: python manage.py runserver")
        sock.close()
    except:
        pass
    
    print("\n🏁 انتهى الاختبار النهائي")

if __name__ == "__main__":
    final_comprehensive_test() 