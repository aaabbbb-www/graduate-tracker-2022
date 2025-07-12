#!/usr/bin/env python
"""
اختبار مبسط لإرسال البريد الإلكتروني
"""
import os
import sys
import django
from datetime import datetime

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_simple_email():
    """اختبار إرسال بريد إلكتروني بسيط"""
    print("🧪 اختبار إرسال بريد إلكتروني بسيط")
    print("=" * 50)
    
    # عرض إعدادات البريد الإلكتروني
    print(f"📧 إعدادات البريد الإلكتروني:")
    print(f"   الخادم: {settings.EMAIL_HOST}")
    print(f"   المنفذ: {settings.EMAIL_PORT}")
    print(f"   المستخدم: {settings.EMAIL_HOST_USER}")
    print(f"   TLS مفعل: {settings.EMAIL_USE_TLS}")
    print()
    
    # رسالة تجريبية
    subject = "اختبار إرسال البريد الإلكتروني - نظام تتبع الخريجين"
    message = """
مرحباً،

هذا اختبار لإرسال البريد الإلكتروني من نظام تتبع الخريجين.

إذا وصلت هذه الرسالة، فهذا يعني أن إعدادات البريد الإلكتروني صحيحة.

تفاصيل الاختبار:
- النظام: نظام تتبع الخريجين
- التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- الحالة: اختبار الإرسال

شكراً لك!

فريق إدارة الخريجين
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['abofars2022p@gmail.com']  # البريد الإلكتروني المطلوب
    
    print(f"📝 تفاصيل الرسالة:")
    print(f"   من: {from_email}")
    print(f"   إلى: {recipient_list}")
    print(f"   الموضوع: {subject}")
    print()
    
    try:
        print("🚀 بدء الإرسال...")
        result = send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ تم إرسال البريد الإلكتروني بنجاح!")
            print(f"   عدد الرسائل المرسلة: {result}")
            print(f"   تم الإرسال إلى: {recipient_list[0]}")
        else:
            print("❌ فشل في إرسال البريد الإلكتروني")
            print(f"   عدد الرسائل المرسلة: {result}")
            
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {str(e)}")
        print()
        print("🔧 نصائح لحل المشكلة:")
        print("   1. تأكد من تحديث إعدادات Gmail في settings.py")
        print("   2. تأكد من تفعيل المصادقة الثنائية")
        print("   3. تأكد من إنشاء كلمة مرور التطبيقات")
        print("   4. تأكد من صحة البريد الإلكتروني وكلمة المرور")

if __name__ == "__main__":
    test_simple_email() 