#!/usr/bin/env python
"""
اختبار إرسال الاستبيان
Test Survey Sending
"""

import os
import sys
import django
from datetime import datetime, timedelta

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduate_system.settings')
django.setup()

from django.contrib.auth.models import User
from surveys.models import Survey, Question, QuestionChoice, Graduate
from surveys.whatsapp_service import EmailService, SurveySender

def create_test_data():
    """إنشاء بيانات تجريبية"""
    print("🔧 إنشاء البيانات التجريبية...")
    
    # إنشاء مستخدم تجريبي
    user, created = User.objects.get_or_create(
        username='test_admin',
        defaults={
            'email': 'test@example.com',
            'first_name': 'مدير',
            'last_name': 'تجريبي',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('test123')
        user.save()
        print("✅ تم إنشاء المستخدم التجريبي")
    
    # إنشاء خريج تجريبي
    graduate, created = Graduate.objects.get_or_create(
        email='abofars2022p@gmail.com',
        defaults={
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'student_id': '2020001',
            'phone': '0501234567',
            'national_id': '1234567890',
            'gender': 'male',
            'birth_date': '1995-01-01',
            'degree': 'bachelor',
            'major': 'علوم الحاسب',
            'college': 'كلية علوم الحاسب',
            'graduation_year': 2023,
            'gpa': 3.75,
            'employment_status': 'employed',
            'company_name': 'شركة التقنية المتقدمة',
            'job_title': 'مطور برمجيات',
            'salary': 8000.00,
            'address': 'الرياض، المملكة العربية السعودية',
            'city': 'الرياض',
            'country': 'السعودية'
        }
    )
    if created:
        print("✅ تم إنشاء الخريج التجريبي")
    
    # إنشاء استبيان تجريبي
    survey, created = Survey.objects.get_or_create(
        title='استبيان رضا الخريجين - اختبار',
        defaults={
            'description': 'نرجو منكم المشاركة في هذا الاستبيان لتقييم البرنامج الأكاديمي ومدى رضاكم عن الخدمات المقدمة.',
            'status': 'active',
            'survey_type': 'custom',
            'created_by': user,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=30),
            'send_method': 'email',
            'email_subject': 'مشاركتك مهمة لنا - استبيان رضا الخريجين',
            'email_message': '''
عزيزي/عزيزتي {graduate.full_name}،

نرجو منك المشاركة في الاستبيان التالي لتقييم البرنامج الأكاديمي:

عنوان الاستبيان: {survey.title}
وصف الاستبيان: {survey.description}

للمشاركة، يرجى النقر على الرابط التالي:
{survey_url}

تاريخ انتهاء الاستبيان: {survey.end_date.strftime('%Y-%m-%d')}

ملاحظات مهمة:
- يمكنك الإجابة على الاستبيان مرة واحدة فقط
- سيتم حفظ إجاباتك بشكل آمن ومجهول
- البيانات ستستخدم لأغراض بحثية وتحليلية فقط

شكراً لك على وقتك ومشاركتك.

مع تحيات،
فريق إدارة الخريجين
            ''',
            'whatsapp_message': '''
مرحباً {graduate.full_name}،

نرجو مشاركتك في استبيان: {survey.title}

{survey.description}

رابط الاستبيان: {survey_url}

ينتهي في: {survey.end_date.strftime('%Y-%m-%d')}

ملاحظات:
• إجابة واحدة فقط
• بيانات آمنة ومجهولة
• لأغراض بحثية فقط

شكراً لك!
            '''
        }
    )
    if created:
        print("✅ تم إنشاء الاستبيان التجريبي")
    
    # إنشاء أسئلة للاستبيان
    questions_data = [
        {
            'question_text': 'ما هو تقييمك العام للبرنامج الأكاديمي؟',
            'question_type': 'rating',
            'is_required': True,
            'order': 1
        },
        {
            'question_text': 'ما هو تخصصك الحالي؟',
            'question_type': 'select',
            'is_required': True,
            'order': 2,
            'choices': ['علوم الحاسب', 'هندسة البرمجيات', 'تقنية المعلومات', 'أمن سيبراني', 'ذكاء اصطناعي']
        },
        {
            'question_text': 'هل أنت راضٍ عن مستوى التدريس؟',
            'question_type': 'radio',
            'is_required': True,
            'order': 3,
            'choices': ['ممتاز', 'جيد جداً', 'جيد', 'مقبول', 'ضعيف']
        },
        {
            'question_text': 'ما هي المجالات التي تحتاج إلى تحسين؟',
            'question_type': 'checkbox',
            'is_required': False,
            'order': 4,
            'choices': ['المختبرات', 'المناهج الدراسية', 'التدريب العملي', 'المرافق', 'الخدمات الطلابية']
        },
        {
            'question_text': 'ما هي اقتراحاتك لتحسين البرنامج؟',
            'question_type': 'textarea',
            'is_required': False,
            'order': 5
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

def test_email_sending():
    """اختبار إرسال البريد الإلكتروني"""
    print("\n📧 اختبار إرسال البريد الإلكتروني...")
    
    # إنشاء البيانات التجريبية
    survey, graduate = create_test_data()
    
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
        else:
            print("❌ فشل في إرسال البريد الإلكتروني")
            print(f"   الخطأ: {result['error']}")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {str(e)}")
    
    # اختبار الإرسال الجماعي
    print(f"\n📬 اختبار الإرسال الجماعي...")
    
    try:
        sender = SurveySender()
        graduates = [graduate]  # قائمة بالخريجين
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

def test_survey_creation():
    """اختبار إنشاء استبيان جديد"""
    print("\n🆕 اختبار إنشاء استبيان جديد...")
    
    try:
        user = User.objects.get(username='test_admin')
        
        # إنشاء استبيان جديد
        new_survey = Survey.objects.create(
            title='استبيان التوظيف - اختبار',
            description='استبيان لتقييم حالة التوظيف لدى الخريجين',
            status='draft',
            survey_type='custom',
            created_by=user,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14),
            send_method='email',
            email_subject='استبيان التوظيف - مشاركتك مهمة',
            email_message='''
مرحباً {graduate.full_name}،

نرجو منك المشاركة في استبيان التوظيف:

{survey.title}
{survey.description}

رابط الاستبيان: {survey_url}

شكراً لك!
            '''
        )
        
        print(f"✅ تم إنشاء استبيان جديد: {new_survey.title}")
        print(f"   الحالة: {new_survey.status}")
        print(f"   طريقة الإرسال: {new_survey.send_method}")
        
        return new_survey
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الاستبيان: {str(e)}")
        return None

def test_survey_sending():
    """اختبار إرسال الاستبيان"""
    print("🔧 اختبار إرسال الاستبيان...")
    
    try:
        # البحث عن استبيان موجود
        survey = Survey.objects.first()
        if not survey:
            print("❌ لا توجد استبيانات في النظام")
            return False
        
        print(f"📋 الاستبيان: {survey.title}")
        
        # البحث عن خريجين
        graduates = Graduate.objects.all()[:3]  # أول 3 خريجين فقط للاختبار
        if not graduates:
            print("❌ لا يوجد خريجين في النظام")
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
        
        if results['whatsapp']:
            whatsapp_success = sum(1 for r in results['whatsapp'] if r['success'])
            whatsapp_failed = len(results['whatsapp']) - whatsapp_success
            print(f"📱 الواتساب: {whatsapp_success} نجح، {whatsapp_failed} فشل")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إرسال الاستبيان: {str(e)}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("🧪 بدء اختبار إرسال الاستبيان")
    print("=" * 60)
    
    # اختبار إنشاء البيانات
    test_email_sending()
    
    # اختبار إنشاء استبيان جديد
    test_survey_creation()
    
    # اختبار إرسال الاستبيان
    test_survey_sending()
    
    print("\n" + "=" * 60)
    print("🏁 انتهى الاختبار")
    print("\n📋 ملاحظات:")
    print("   - تأكد من إعدادات SMTP في settings.py")
    print("   - تأكد من صحة بيانات Gmail")
    print("   - تحقق من كلمة مرور التطبيقات")
    print("   - راجع سجلات الأخطاء إذا فشل الإرسال")

if __name__ == "__main__":
    main() 