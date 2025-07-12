"""
Google Forms Integration Module
إدارة التكامل مع Google Forms وGoogle Sheets
"""

import os
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from django.core.cache import cache


class GoogleFormsIntegration:
    """فئة لإدارة التكامل مع Google Forms"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/forms',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.creds = None
        self.forms_service = None
        self.sheets_service = None
        self.drive_service = None
    
    def authenticate(self):
        """المصادقة مع Google API"""
        token_path = os.path.join(settings.BASE_DIR, 'credentials', 'token.json')
        creds_path = os.path.join(settings.BASE_DIR, 'credentials', 'credentials.json')
        
        # تحميل الرمز المميز المحفوظ
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # إذا لم تكن هناك رموز مميزة صالحة، احصل على رموز جديدة
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # حفظ الرموز المميزة للاستخدام التالي
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())
        
        # إنشاء خدمات API
        self.forms_service = build('forms', 'v1', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
    
    def create_survey_from_template(self, template_id, title, description, questions_data):
        """إنشاء استبيان من قالب جاهز"""
        try:
            self.authenticate()
            
            # نسخ القالب
            copied_form = self.drive_service.files().copy(
                fileId=template_id,
                body={'name': title}
            ).execute()
            
            form_id = copied_form['id']
            
            # تحديث عنوان ووصف النموذج
            self.forms_service.forms().update(
                formId=form_id,
                body={
                    'info': {
                        'title': title,
                        'description': description
                    }
                }
            ).execute()
            
            # إضافة الأسئلة المخصصة
            if questions_data:
                self._add_custom_questions(form_id, questions_data)
            
            return {
                'success': True,
                'form_id': form_id,
                'form_url': f'https://forms.google.com/forms/d/{form_id}',
                'edit_url': f'https://forms.google.com/forms/d/{form_id}/edit'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_custom_questions(self, form_id, questions_data):
        """إضافة أسئلة مخصصة للنموذج"""
        requests = []
        
        for question_data in questions_data:
            request = self._create_question_request(question_data)
            if request:
                requests.append(request)
        
        if requests:
            self.forms_service.forms().batchUpdate(
                formId=form_id,
                body={'requests': requests}
            ).execute()
    
    def _create_question_request(self, question_data):
        """إنشاء طلب إضافة سؤال"""
        question_type = question_data.get('type', 'textQuestion')
        
        if question_type == 'textQuestion':
            return {
                'createItem': {
                    'item': {
                        'title': question_data['title'],
                        'questionItem': {
                            'question': {
                                'textQuestion': {
                                    'paragraph': question_data.get('paragraph', False)
                                }
                            }
                        }
                    },
                    'location': {
                        'index': question_data.get('index', 0)
                    }
                }
            }
        
        elif question_type == 'choiceQuestion':
            return {
                'createItem': {
                    'item': {
                        'title': question_data['title'],
                        'questionItem': {
                            'question': {
                                'choiceQuestion': {
                                    'type': question_data.get('choice_type', 'RADIO'),
                                    'options': [
                                        {'value': choice} for choice in question_data['choices']
                                    ]
                                }
                            }
                        }
                    },
                    'location': {
                        'index': question_data.get('index', 0)
                    }
                }
            }
        
        return None
    
    def get_survey_responses(self, form_id, spreadsheet_id=None):
        """الحصول على استجابات الاستبيان"""
        try:
            self.authenticate()
            
            # الحصول على الاستجابات
            responses = self.forms_service.forms().responses().list(
                formId=form_id
            ).execute()
            
            # إذا كان هناك جدول بيانات مرتبط، احصل على البيانات منه
            if spreadsheet_id:
                sheet_data = self.sheets_service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='A:Z'
                ).execute()
                
                return {
                    'success': True,
                    'responses': responses.get('responses', []),
                    'sheet_data': sheet_data.get('values', [])
                }
            
            return {
                'success': True,
                'responses': responses.get('responses', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_response_spreadsheet(self, form_id, title):
        """إنشاء جدول بيانات لاستجابات الاستبيان"""
        try:
            self.authenticate()
            
            # إنشاء جدول بيانات جديد
            spreadsheet = {
                'properties': {
                    'title': f'استجابات {title}'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'الاستجابات'
                        }
                    }
                ]
            }
            
            created_spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet
            ).execute()
            
            spreadsheet_id = created_spreadsheet['spreadsheetId']
            
            # ربط النموذج بجدول البيانات
            self.forms_service.forms().update(
                formId=form_id,
                body={
                    'linkedSheetId': spreadsheet_id
                }
            ).execute()
            
            return {
                'success': True,
                'spreadsheet_id': spreadsheet_id,
                'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# قوالب الاستبيانات الجاهزة
SURVEY_TEMPLATES = {
    'employment_survey': {
        'id': '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',  # مثال
        'name': 'استبيان التوظيف',
        'description': 'استبيان لتقييم حالة التوظيف للخريجين',
        'questions': [
            {
                'title': 'هل أنت موظف حالياً؟',
                'type': 'choiceQuestion',
                'choice_type': 'RADIO',
                'choices': ['نعم', 'لا']
            },
            {
                'title': 'ما هو مجال عملك؟',
                'type': 'textQuestion',
                'paragraph': False
            },
            {
                'title': 'ما هو راتبك الشهري؟',
                'type': 'choiceQuestion',
                'choice_type': 'RADIO',
                'choices': ['أقل من 5000', '5000-10000', '10000-15000', 'أكثر من 15000']
            }
        ]
    },
    'satisfaction_survey': {
        'id': '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',  # مثال
        'name': 'استبيان رضا الخريجين',
        'description': 'استبيان لقياس رضا الخريجين عن البرنامج التعليمي',
        'questions': [
            {
                'title': 'ما هو تقييمك العام للبرنامج التعليمي؟',
                'type': 'choiceQuestion',
                'choice_type': 'RADIO',
                'choices': ['ممتاز', 'جيد جداً', 'جيد', 'مقبول', 'ضعيف']
            },
            {
                'title': 'ما هي نقاط القوة في البرنامج؟',
                'type': 'textQuestion',
                'paragraph': True
            },
            {
                'title': 'ما هي نقاط الضعف التي تحتاج تحسين؟',
                'type': 'textQuestion',
                'paragraph': True
            }
        ]
    },
    'career_development': {
        'id': '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',  # مثال
        'name': 'استبيان التطوير المهني',
        'description': 'استبيان لتقييم احتياجات التطوير المهني',
        'questions': [
            {
                'title': 'ما هي المهارات التي تحتاج تطويرها؟',
                'type': 'choiceQuestion',
                'choice_type': 'CHECKBOX',
                'choices': ['القيادة', 'التواصل', 'التقنية', 'الإدارة', 'اللغة الإنجليزية']
            },
            {
                'title': 'ما هي الدورات التدريبية التي تفضل؟',
                'type': 'textQuestion',
                'paragraph': True
            },
            {
                'title': 'هل ترغب في الحصول على شهادات مهنية؟',
                'type': 'choiceQuestion',
                'choice_type': 'RADIO',
                'choices': ['نعم', 'لا', 'ربما']
            }
        ]
    }
} 