"""
WhatsApp Service for Survey Sending
خدمة إرسال الواتساب للاستبيانات
"""

import requests
import json
from django.conf import settings
from django.core.cache import cache


class WhatsAppService:
    """خدمة إرسال رسائل الواتساب"""
    
    def __init__(self):
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0')
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
    
    def send_message(self, phone_number, message):
        """إرسال رسالة واتساب"""
        try:
            # تنظيف رقم الهاتف
            phone_number = self._clean_phone_number(phone_number)
            
            # إعداد الرسالة
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            # إرسال الطلب
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.api_url}/{self.phone_number_id}/messages',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json().get('messages', [{}])[0].get('id'),
                    'response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'response': response.json() if response.text else None
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_survey_message(self, phone_number, survey, graduate):
        """إرسال رسالة استبيان عبر الواتساب"""
        message = survey.get_whatsapp_message(graduate)
        return self.send_message(phone_number, message)
    
    def _clean_phone_number(self, phone_number):
        """تنظيف رقم الهاتف"""
        # إزالة المسافات والرموز
        cleaned = ''.join(filter(str.isdigit, str(phone_number)))
        
        # إضافة رمز البلد إذا لم يكن موجوداً
        if not cleaned.startswith('966'):
            if cleaned.startswith('0'):
                cleaned = '966' + cleaned[1:]
            else:
                cleaned = '966' + cleaned
        
        return cleaned
    
    def is_configured(self):
        """التحقق من إعداد الخدمة"""
        return bool(self.access_token and self.phone_number_id)


class MockWhatsAppService:
    """خدمة واتساب تجريبية للاختبار"""
    
    def __init__(self):
        self.sent_messages = []
    
    def send_message(self, phone_number, message):
        """محاكاة إرسال رسالة واتساب"""
        self.sent_messages.append({
            'phone_number': phone_number,
            'message': message,
            'timestamp': '2025-07-02 10:30:00'
        })
        
        return {
            'success': True,
            'message_id': f'mock_{len(self.sent_messages)}',
            'response': {'status': 'mock_sent'}
        }
    
    def send_survey_message(self, phone_number, survey, graduate):
        """محاكاة إرسال رسالة استبيان"""
        message = survey.get_whatsapp_message(graduate)
        return self.send_message(phone_number, message)
    
    def is_configured(self):
        """دائماً متاح للاختبار"""
        return True


# اختيار الخدمة المناسبة
def get_whatsapp_service():
    """الحصول على خدمة الواتساب المناسبة"""
    if getattr(settings, 'WHATSAPP_ACCESS_TOKEN', ''):
        return WhatsAppService()
    else:
        return MockWhatsAppService()


class EmailService:
    """خدمة إرسال البريد الإلكتروني"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    
    def send_survey_email(self, survey, graduate, request=None):
        """إرسال استبيان عبر البريد الإلكتروني"""
        try:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            
            subject = survey.get_email_subject()
            message = survey.get_email_message(graduate)
            
            # إذا كان هناك رابط مطلق، استخدمه
            if request and not survey.google_form_url:
                survey_url = request.build_absolute_uri(f'/surveys/{survey.pk}/take/')
                message = message.replace(f'/surveys/{survey.pk}/take/', survey_url)
            
            # إرسال البريد الإلكتروني
            send_mail(
                subject,
                message,
                self.from_email,
                [graduate.email],
                fail_silently=False,
            )
            
            return {
                'success': True,
                'message': 'تم إرسال البريد الإلكتروني بنجاح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_survey_to_graduates(self, survey, graduates, request=None):
        """إرسال استبيان لجميع الخريجين عبر البريد الإلكتروني"""
        results = []
        
        for graduate in graduates:
            if not graduate.email:
                results.append({
                    'graduate': graduate,
                    'success': False,
                    'error': 'لا يوجد بريد إلكتروني'
                })
                continue
            
            result = self.send_survey_email(survey, graduate, request)
            results.append({
                'graduate': graduate,
                'success': result['success'],
                'error': result.get('error')
            })
        
        return results


class SurveySender:
    """فئة رئيسية لإرسال الاستبيانات"""
    
    def __init__(self):
        self.whatsapp_service = get_whatsapp_service()
        self.email_service = EmailService()
    
    def send_survey(self, survey, graduates, request=None):
        """إرسال استبيان بالطريقة المحددة"""
        results = {
            'email': [],
            'whatsapp': [],
            'total_sent': 0,
            'total_failed': 0
        }
        
        if survey.send_method in ['email', 'both']:
            email_results = self.email_service.send_survey_to_graduates(survey, graduates, request)
            results['email'] = email_results
            
            for result in email_results:
                if result['success']:
                    results['total_sent'] += 1
                else:
                    results['total_failed'] += 1
        
        if survey.send_method in ['whatsapp', 'both']:
            whatsapp_results = self.whatsapp_service.send_survey_to_graduates(survey, graduates)
            results['whatsapp'] = whatsapp_results
            
            for result in whatsapp_results:
                if result['success']:
                    results['total_sent'] += 1
                else:
                    results['total_failed'] += 1
        
        return results 