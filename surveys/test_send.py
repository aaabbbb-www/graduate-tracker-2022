#!/usr/bin/env python
"""
ملف اختبار لنظام الإرسال
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from surveys.models import Survey, SurveySendLog
from graduates.models import Graduate

def test_send_survey():
    """اختبار إرسال استبيان"""
    try:
        # الحصول على أول استبيان
        survey = Survey.objects.first()
        if not survey:
            print("لا توجد استبيانات في النظام")
            return
        
        # الحصول على أول خريج
        graduate = Graduate.objects.first()
        if not graduate:
            print("لا توجد خريجين في النظام")
            return
        
        print(f"اختبار إرسال الاستبيان: {survey.title}")
        print(f"إلى الخريج: {graduate.full_name}")
        print(f"البريد الإلكتروني: {graduate.email}")
        print(f"الهاتف: {graduate.phone}")
        
        # تسجيل إرسال تجريبي
        log = SurveySendLog.objects.create(
            survey=survey,
            graduate=graduate,
            send_method='email',
            status='sent'
        )
        
        print(f"تم تسجيل الإرسال بنجاح: {log}")
        
        # عرض رسالة البريد الإلكتروني
        email_message = survey.get_email_message(graduate)
        print("\nرسالة البريد الإلكتروني:")
        print("=" * 50)
        print(email_message)
        print("=" * 50)
        
        # عرض رسالة الواتساب
        whatsapp_message = survey.get_whatsapp_message(graduate)
        print("\nرسالة الواتساب:")
        print("=" * 50)
        print(whatsapp_message)
        print("=" * 50)
        
    except Exception as e:
        print(f"خطأ في الاختبار: {str(e)}")

if __name__ == "__main__":
    test_send_survey() 