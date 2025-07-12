#!/usr/bin/env python
"""
اختبار إرسال استبيان إلى abofars2022p@gmail.com
"""
import os
import sys
import django
from datetime import datetime, timedelta

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from django.contrib.auth.models import User
from surveys.models import Survey, Question, QuestionChoice
from graduates.models import Graduate
from surveys.whatsapp_service import EmailService, SurveySender

def create_survey_for_abofars():
    """إنشاء استبيان خاص لـ abofars2022p@gmail.com"""
    print("🎯 إنشاء استبيان خاص لـ abofars2022p@gmail.com")
    print("=" * 60)
    
    # إنشاء مستخدم تجريبي
    user, created = User.objects.get_or_create(
        username='test_admin',
        defaults={
            'email': 'admin@graduate-tracker.com',
            'first_name': 'مدير',
            'last_name': 'النظام',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('test123')
        user.save()
        print("✅ تم إنشاء المستخدم التجريبي")
    
    # إنشاء خريج abofars
    graduate, created = Graduate.objects.get_or_create(
        email='abofars2022p@gmail.com',
        defaults={
            'first_name': 'أبو',
            'last_name': 'فارس',
            'student_id': '2024001',
            'phone': '0501234567',
            'national_id': '1234567891',
            'gender': 'male',
            'birth_date': '1990-01-01',
            'degree': 'bachelor',
            'major': 'علوم الحاسب',
            'college': 'كلية علوم الحاسب',
            'graduation_year': 2024,
            'gpa': 3.85,
            'employment_status': 'employed',
            'company_name': 'شركة التقنية المتقدمة',
            'job_title': 'مطور برمجيات',
            'salary': 10000.00,
            'address': 'الرياض، المملكة العربية السعودية',
            'city': 'الرياض',
            'country': 'السعودية'
        }
    )
    if created:
        print("✅ تم إنشاء الخريج abofars")
    else:
        print("✅ الخريج abofars موجود بالفعل")
    
    # إنشاء استبيان خاص
    survey, created = Survey.objects.get_or_create(
        title='استبيان خاص - اختبار النظام',
        defaults={
            'description': 'هذا استبيان تجريبي لاختبار نظام إرسال البريد الإلكتروني في نظام تتبع الخريجين.',
            'status': 'active',
            'survey_type': 'custom',
            'created_by': user,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=30),
            'send_method': 'email',
            'email_subject': 'استبيان خاص - اختبار نظام تتبع الخريجين',
            'email_message': '''
عزيزي/عزيزتي {graduate.full_name}،

مرحباً بك في اختبار نظام تتبع الخريجين!

نرجو منك المشاركة في الاستبيان التالي:

عنوان الاستبيان: {survey.title}
وصف الاستبيان: {survey.description}

للمشاركة، يرجى النقر على الرابط التالي:
{survey_url}

تفاصيل الاختبار:
- تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- نوع الاختبار: إرسال البريد الإلكتروني
- النظام: نظام تتبع الخريجين

تاريخ انتهاء الاستبيان: {survey.end_date.strftime('%Y-%m-%d')}

ملاحظات مهمة:
- يمكنك الإجابة على الاستبيان مرة واحدة فقط
- سيتم حفظ إجاباتك بشكل آمن ومجهول
- البيانات ستستخدم لأغراض اختبار النظام فقط

شكراً لك على مشاركتك في اختبار النظام!

مع تحيات،
فريق تطوير نظام تتبع الخريجين
            ''',
            'whatsapp_message': '''
مرحباً {graduate.full_name}،

هذا اختبار لنظام تتبع الخريجين!

استبيان: {survey.title}
{survey.description}

رابط الاستبيان: {survey_url}

ينتهي في: {survey.end_date.strftime('%Y-%m-%d')}

شكراً لك!
            '''
        }
    )
    if created:
        print("✅ تم إنشاء الاستبيان الخاص")
    else:
        print("✅ الاستبيان الخاص موجود بالفعل")
    
    # إنشاء أسئلة للاستبيان
    questions_data = [
        {
            'question_text': 'هل يعمل نظام إرسال البريد الإلكتروني بشكل صحيح؟',
            'question_type': 'radio',
            'is_required': True,
            'order': 1,
            'choices': ['نعم، يعمل بشكل ممتاز', 'نعم، يعمل بشكل جيد', 'يحتاج تحسين', 'لا يعمل']
        },
        {
            'question_text': 'ما هو تقييمك لواجهة النظام؟',
            'question_type': 'rating',
            'is_required': True,
            'order': 2
        },
        {
            'question_text': 'ما هي الميزات التي تريد إضافتها للنظام؟',
            'question_type': 'checkbox',
            'is_required': False,
            'order': 3,
            'choices': ['تطبيق الهاتف المحمول', 'تقارير متقدمة', 'تكامل مع وسائل التواصل', 'ذكاء اصطناعي', 'واجهة محسنة']
        },
        {
            'question_text': 'ما هي اقتراحاتك لتحسين النظام؟',
            'question_type': 'textarea',
            'is_required': False,
            'order': 4
        },
        {
            'question_text': 'هل توصي باستخدام هذا النظام؟',
            'question_type': 'radio',
            'is_required': True,
            'order': 5,
            'choices': ['نعم، بالتأكيد', 'نعم، مع بعض التحسينات', 'ربما', 'لا']
        }
    ]
    
    for q_data in questions_data:
        question, created = Question.objects.get_or_create(
            survey=survey,
            question_text=q_data['question_text'],
            defaults={
                'question_type': q_data['question_type'],
                'is_required': q_data['is_required'],
                'order': q_data['order']
            }
        )
        
        if created and 'choices' in q_data:
            for i, choice_text in enumerate(q_data['choices']):
                QuestionChoice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    order=i + 1
                )
    
    print("✅ تم إنشاء أسئلة الاستبيان")
    
    return survey, graduate

def test_send_to_abofars():
    """اختبار إرسال استبيان إلى abofars2022p@gmail.com"""
    print("\n📧 اختبار إرسال استبيان إلى abofars2022p@gmail.com")
    print("=" * 60)
    
    # إنشاء البيانات
    survey, graduate = create_survey_for_abofars()
    
    # عرض معلومات الاختبار
    print(f"\n📋 معلومات الاختبار:")
    print(f"   الاستبيان: {survey.title}")
    print(f"   الخريج: {graduate.full_name}")
    print(f"   البريد الإلكتروني: {graduate.email}")
    print(f"   طريقة الإرسال: {survey.send_method}")
    
    # عرض رسالة البريد الإلكتروني
    print(f"\n📝 رسالة البريد الإلكتروني:")
    print("=" * 60)
    subject = survey.get_email_subject()
    message = survey.get_email_message(graduate)
    print(f"الموضوع: {subject}")
    print(f"الرسالة:\n{message}")
    print("=" * 60)
    
    # اختبار إرسال البريد الإلكتروني
    print(f"\n🚀 بدء اختبار الإرسال...")
    
    try:
        email_service = EmailService()
        result = email_service.send_survey_email(survey, graduate)
        
        if result['success']:
            print("✅ تم إرسال البريد الإلكتروني بنجاح!")
            print(f"   الرسالة: {result['message']}")
            print(f"   تم الإرسال إلى: {graduate.email}")
        else:
            print("❌ فشل في إرسال البريد الإلكتروني")
            print(f"   الخطأ: {result['error']}")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {str(e)}")
    
    # اختبار الإرسال الجماعي
    print(f"\n📬 اختبار الإرسال الجماعي...")
    
    try:
        sender = SurveySender()
        graduates = [graduate]
        results = sender.send_survey(survey, graduates)
        
        print(f"📊 نتائج الإرسال الجماعي:")
        print(f"   إجمالي المرسل إليهم: {results['total_sent']}")
        print(f"   إجمالي الفاشل: {results['total_failed']}")
        
        if results['email']:
            email_results = results['email']
            success_count = sum(1 for r in email_results if r['success'])
            failed_count = len(email_results) - success_count
            
            print(f"   رسائل البريد الناجحة: {success_count}")
            print(f"   رسائل البريد الفاشلة: {failed_count}")
            
            for result in email_results:
                if result['success']:
                    print(f"   ✅ {result['graduate'].full_name}: تم الإرسال بنجاح")
                else:
                    print(f"   ❌ {result['graduate'].full_name}: {result['error']}")
                    
    except Exception as e:
        print(f"❌ خطأ في الإرسال الجماعي: {str(e)}")

def main():
    """الدالة الرئيسية للاختبار"""
    print("🎯 اختبار إرسال استبيان إلى abofars2022p@gmail.com")
    print("=" * 60)
    
    test_send_to_abofars()
    
    print("\n" + "=" * 60)
    print("🏁 انتهى الاختبار")
    print("\n📋 ملاحظات:")
    print("   - تحقق من بريدك الإلكتروني: abofars2022p@gmail.com")
    print("   - تأكد من إعدادات SMTP في settings.py")
    print("   - تأكد من تفعيل المصادقة الثنائية في Gmail")
    print("   - استخدم كلمة مرور التطبيقات وليس كلمة مرور الحساب")

if __name__ == "__main__":
    main() 