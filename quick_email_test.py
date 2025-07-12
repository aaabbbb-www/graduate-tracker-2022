#!/usr/bin/env python
"""
اختبار سريع للبريد الإلكتروني
Quick Email Test
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def quick_email_test():
    """اختبار سريع للبريد الإلكتروني"""
    print("🔧 اختبار سريع للبريد الإلكتروني...")
    print(f"📧 من: {settings.EMAIL_HOST_USER}")
    print(f"🌐 الخادم: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"🔐 TLS: {settings.EMAIL_USE_TLS}")
    
    try:
        # إرسال بريد إلكتروني تجريبي
        subject = "اختبار إرسال الاستبيانات - Graduate Tracker"
        message = """
        مرحباً!
        
        هذا بريد إلكتروني تجريبي لاختبار إعدادات إرسال الاستبيانات.
        
        إذا وصل هذا البريد، فهذا يعني أن الإعدادات صحيحة.
        
        شكراً لك!
        """
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # إرسال لنفس البريد
            fail_silently=False,
        )
        
        if result:
            print("✅ تم إرسال البريد الإلكتروني بنجاح!")
            print("📬 تحقق من صندوق الوارد الخاص بك")
            print("💡 إذا لم تصل الرسالة، تحقق من:")
            print("   1. إعدادات Gmail")
            print("   2. كلمة مرور التطبيقات")
            print("   3. تفعيل المصادقة الثنائية")
            return True
        else:
            print("❌ فشل في إرسال البريد الإلكتروني")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إرسال البريد الإلكتروني: {str(e)}")
        print("\n🔍 نصائح لحل المشكلة:")
        print("1. تأكد من تفعيل المصادقة الثنائية في Gmail")
        print("2. تأكد من استخدام كلمة مرور التطبيقات وليس كلمة مرور الحساب")
        print("3. تأكد من صحة البريد الإلكتروني وكلمة المرور")
        print("4. تحقق من إعدادات الجدار الناري")
        return False

if __name__ == "__main__":
    quick_email_test() 