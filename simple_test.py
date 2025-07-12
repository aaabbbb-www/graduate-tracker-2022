#!/usr/bin/env python
"""
اختبار بسيط لإرسال الاستبيان
Simple Survey Sending Test
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from surveys.models import Survey
from graduates.models import Graduate
from surveys.whatsapp_service import SurveySender

def test_survey_sending():
    """اختبار إرسال الاستبيان"""
    print("🔧 اختبار إرسال الاستبيان...")
    
    try:
        # البحث عن استبيان موجود
        survey = Survey.objects.first()
        if not survey:
            print("❌ لا توجد استبيانات في النظام")
            print("💡 قم بإنشاء استبيان أولاً من خلال الواجهة")
            return False
        
        print(f"📋 الاستبيان: {survey.title}")
        
        # البحث عن خريجين
        graduates = Graduate.objects.all()[:3]  # أول 3 خريجين فقط للاختبار
        if not graduates:
            print("❌ لا يوجد خريجين في النظام")
            print("💡 قم بإضافة خريجين أولاً من خلال الواجهة")
            return False
        
        print(f"👥 عدد الخريجين: {graduates.count()}")
        
        # إرسال الاستبيان
        sender = SurveySender()
        results = sender.send_survey(survey, graduates)
        
        print(f"✅ تم إرسال {results['total_sent']} استبيان بنجاح")
        print(f"❌ فشل في إرسال {results['total_failed']} استبيان")
        
        if results['email']:
            email_success = sum(1 for r in results['email'] if r['success'])
            email_failed = len(results['email']) - email_success
            print(f"📧 البريد الإلكتروني: {email_success} نجح، {email_failed} فشل")
            
            # عرض تفاصيل الأخطاء
            for result in results['email']:
                if not result['success']:
                    print(f"   ❌ {result['graduate'].full_name}: {result.get('error', 'خطأ غير معروف')}")
        
        if results['whatsapp']:
            whatsapp_success = sum(1 for r in results['whatsapp'] if r['success'])
            whatsapp_failed = len(results['whatsapp']) - whatsapp_success
            print(f"📱 الواتساب: {whatsapp_success} نجح، {whatsapp_failed} فشل")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إرسال الاستبيان: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_survey_sending() 