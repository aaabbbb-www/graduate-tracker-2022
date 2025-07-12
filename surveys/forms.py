from django import forms
from django.core.exceptions import ValidationError
from .models import Survey, Question, QuestionChoice, SurveyResponse, Answer, SurveyTemplate
from graduates.models import Graduate
from datetime import datetime


class FlexibleSurveyForm(forms.ModelForm):
    """نموذج محسن لإنشاء استبيان مرن"""
    
    # معلومات أساسية
    title = forms.CharField(
        max_length=200,
        label='عنوان الاستبيان',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: استبيان رضا الخريجين عن البرنامج الأكاديمي'
        }),
        help_text='اكتب عنوان واضح ومختصر للاستبيان'
    )
    
    description = forms.CharField(
        label='وصف الاستبيان',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'اكتب وصفاً مفصلاً للاستبيان وأهدافه'
        }),
        help_text='اشرح الغرض من الاستبيان وما تريد تحقيقه'
    )
    
    # إعدادات الاستبيان
    status = forms.ChoiceField(
        choices=Survey.SURVEY_STATUS_CHOICES,
        label='حالة الاستبيان',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='اختر حالة الاستبيان'
    )
    
    # تواريخ الاستبيان
    start_date = forms.DateTimeField(
        label='تاريخ بداية الاستبيان',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        help_text='متى سيبدأ الاستبيان'
    )
    
    end_date = forms.DateTimeField(
        label='تاريخ انتهاء الاستبيان',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        help_text='متى سينتهي الاستبيان'
    )
    
    # إعدادات الإرسال
    send_method = forms.ChoiceField(
        choices=Survey.SEND_METHOD_CHOICES,
        label='طريقة الإرسال',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='اختر طريقة إرسال الاستبيان للخريجين'
    )
    
    auto_send = forms.BooleanField(
        required=False,
        label='إرسال تلقائي بعد الإنشاء',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='إرسال الاستبيان للخريجين تلقائياً بعد الإنشاء'
    )
    
    # رسائل مخصصة
    email_subject = forms.CharField(
        max_length=200,
        required=False,
        label='موضوع البريد الإلكتروني',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اتركه فارغاً لاستخدام العنوان الافتراضي'
        }),
        help_text='موضوع رسالة البريد الإلكتروني'
    )
    
    email_message = forms.CharField(
        required=False,
        label='رسالة البريد الإلكتروني',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'اتركه فارغاً لاستخدام الرسالة الافتراضية'
        }),
        help_text='رسالة البريد الإلكتروني المخصصة'
    )
    
    whatsapp_message = forms.CharField(
        required=False,
        label='رسالة الواتساب',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'اتركه فارغاً لاستخدام الرسالة الافتراضية'
        }),
        help_text='رسالة الواتساب المخصصة'
    )
    
    # اختيار الخريجين
    target_college = forms.CharField(
        max_length=100,
        required=False,
        label='الكلية المستهدفة',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: كلية الحاسبات والمعلومات'
        }),
        help_text='اكتب اسم الكلية التي تريد إرسال الاستبيان إلى خريجيها'
    )
    
    selected_graduates = forms.ModelMultipleChoiceField(
        queryset=Graduate.objects.filter(is_active=True),
        required=False,
        label='اختر الخريجين',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='اختر الخريجين الذين سيتم إرسال الاستبيان إليهم'
    )
    
    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'status', 'start_date', 'end_date',
            'send_method', 'auto_send', 'email_subject', 'email_message',
            'whatsapp_message', 'target_college', 'selected_graduates'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعيين قيم افتراضية للتواريخ
        if not self.instance.pk:
            from django.utils import timezone
            from datetime import timedelta
            
            now = timezone.now()
            end_date = now + timedelta(days=30)
            
            self.fields['start_date'].initial = now.strftime('%Y-%m-%dT%H:%M')
            self.fields['end_date'].initial = end_date.strftime('%Y-%m-%dT%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
        
        return cleaned_data


class FlexibleQuestionForm(forms.ModelForm):
    """نموذج محسن لإنشاء أسئلة مرنة"""
    
    question_text = forms.CharField(
        label='نص السؤال',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'اكتب السؤال هنا...'
        }),
        help_text='اكتب السؤال بوضوح'
    )
    
    question_type = forms.ChoiceField(
        choices=Question.QUESTION_TYPES,
        label='نوع السؤال',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='اختر نوع السؤال المناسب'
    )
    
    is_required = forms.BooleanField(
        required=False,
        label='سؤال مطلوب',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='هل هذا السؤال إجباري؟'
    )
    
    help_text = forms.CharField(
        max_length=200,
        required=False,
        label='نص المساعدة',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نص مساعدة اختياري'
        }),
        help_text='نص مساعدة للمستجيب'
    )
    
    # حقول إضافية للخيارات
    choices_text = forms.CharField(
        required=False,
        label='الخيارات (سطر واحد لكل خيار)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'اكتب كل خيار في سطر منفصل\nمثال:\nخيار 1\nخيار 2\nخيار 3'
        }),
        help_text='اكتب الخيارات (للأسئلة من نوع اختيار)'
    )
    
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'is_required', 'help_text']
    
    def clean_choices_text(self):
        """تنظيف وتحقق من الخيارات"""
        choices_text = self.cleaned_data.get('choices_text')
        question_type = self.cleaned_data.get('question_type')
        
        if question_type in ['radio', 'checkbox', 'select'] and not choices_text:
            raise forms.ValidationError('يجب إضافة خيارات للأسئلة من نوع اختيار')
        
        return choices_text


class SurveyForm(forms.ModelForm):
    """نموذج إنشاء وتعديل الاستبيان"""
    
    # حقول إرسال الاستبيان
    auto_send = forms.BooleanField(
        required=False,
        label='إرسال تلقائي بعد الإنشاء',
        help_text='إرسال الاستبيان للخريجين تلقائياً بعد الإنشاء'
    )
    
    send_method = forms.ChoiceField(
        choices=Survey.SEND_METHOD_CHOICES,
        label='طريقة الإرسال',
        help_text='اختر طريقة إرسال الاستبيان'
    )
    
    email_subject = forms.CharField(
        max_length=200,
        required=False,
        label='موضوع البريد الإلكتروني',
        help_text='اتركه فارغاً لاستخدام العنوان الافتراضي'
    )
    
    email_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        required=False,
        label='رسالة البريد الإلكتروني',
        help_text='اتركه فارغاً لاستخدام الرسالة الافتراضية'
    )
    
    whatsapp_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        required=False,
        label='رسالة الواتساب',
        help_text='اتركه فارغاً لاستخدام الرسالة الافتراضية'
    )
    
    target_college = forms.CharField(
        max_length=100,
        required=False,
        label='الكلية المستهدفة',
        help_text='اكتب اسم الكلية التي تريد إرسال الاستبيان إلى خريجيها (مثال: كلية الحاسبات)'
    )
    
    # حقول اختيار الخريجين
    selected_graduates = forms.ModelMultipleChoiceField(
        queryset=Graduate.objects.filter(is_active=True),
        required=False,
        label='اختر الخريجين',
        help_text='اختر الخريجين الذين سيتم إرسال الاستبيان إليهم',
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'start_date', 'end_date', 
            'google_form_url', 'status', 'send_method', 'auto_send',
            'email_subject', 'email_message', 'whatsapp_message', 'target_college', 
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'google_form_url': forms.URLInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'send_method': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعيين قيم افتراضية للتواريخ
        if not self.instance.pk:
            from django.utils import timezone
            from datetime import timedelta
            
            now = timezone.now()
            end_date = now + timedelta(days=30)
            
            self.fields['start_date'].initial = now.strftime('%Y-%m-%dT%H:%M')
            self.fields['end_date'].initial = end_date.strftime('%Y-%m-%dT%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
        
        return cleaned_data


class QuestionForm(forms.ModelForm):
    """نموذج إنشاء وتعديل السؤال"""
    
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'is_required', 'help_text']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'help_text': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SurveyResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super().__init__(*args, **kwargs)
        
        for question in questions:
            field_name = f'question_{question.id}'
            
            if question.question_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            
            elif question.question_type == 'textarea':
                self.fields[field_name] = forms.CharField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
                )
            
            elif question.question_type == 'email':
                self.fields[field_name] = forms.EmailField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.EmailInput(attrs={'class': 'form-control'})
                )
            
            elif question.question_type == 'number':
                self.fields[field_name] = forms.DecimalField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
            
            elif question.question_type == 'date':
                self.fields[field_name] = forms.DateField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                )
            
            elif question.question_type == 'radio':
                choices = [(choice.id, choice.choice_text) for choice in question.choices.all()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                )
            
            elif question.question_type == 'checkbox':
                choices = [(choice.id, choice.choice_text) for choice in question.choices.all()]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                )
            
            elif question.question_type == 'select':
                choices = [('', 'اختر...')] + [(choice.id, choice.choice_text) for choice in question.choices.all()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            
            elif question.question_type == 'rating':
                choices = [(i, str(i)) for i in range(1, 6)]  # تقييم من 1 إلى 5
                self.fields[field_name] = forms.ChoiceField(
                    label=question.question_text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                )


class SendSurveyForm(forms.Form):
    """نموذج إرسال الاستبيان"""
    
    survey = forms.ModelChoiceField(
        queryset=Survey.objects.filter(status='active'),
        label='اختر الاستبيان',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    graduates = forms.ModelMultipleChoiceField(
        queryset=Graduate.objects.filter(is_active=True),
        label='اختر الخريجين',
        widget=forms.CheckboxSelectMultiple
    )
    
    send_method = forms.ChoiceField(
        choices=Survey.SEND_METHOD_CHOICES,
        label='طريقة الإرسال',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    custom_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='رسالة مخصصة',
        help_text='رسالة إضافية مع الاستبيان'
    )


class QuickSurveyForm(forms.Form):
    """نموذج لإنشاء استبيان سريع"""
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'عنوان الاستبيان'
        })
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'وصف مختصر للاستبيان'
        })
    )
    
    questions_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'اكتب الأسئلة، سطر واحد لكل سؤال\nمثال:\nما هو تقييمك للبرنامج؟\nما هي اقتراحاتك للتحسين؟'
        }),
        help_text='اكتب الأسئلة، سطر واحد لكل سؤال'
    )
    
    def clean_questions_text(self):
        questions_text = self.cleaned_data.get('questions_text')
        if not questions_text.strip():
            raise forms.ValidationError('يجب إضافة أسئلة للاستبيان')
        
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        if len(questions) < 1:
            raise forms.ValidationError('يجب إضافة سؤال واحد على الأقل')
        
        return questions_text


class SurveyFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'جميع الحالات')] + Survey.SURVEY_STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في العنوان أو الوصف'
        })
    )
    
    created_by = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='أنشئ بواسطة',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        label='من تاريخ',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class ChoiceForm(forms.ModelForm):
    """نموذج إضافة خيار للسؤال"""
    
    class Meta:
        model = QuestionChoice
        fields = ['choice_text']
        widgets = {
            'choice_text': forms.TextInput(attrs={'class': 'form-control'})
        }


class SurveyTemplateForm(forms.ModelForm):
    """نموذج قالب الاستبيان"""
    
    class Meta:
        model = SurveyTemplate
        fields = ['title', 'description', 'category', 'difficulty', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NewSurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['org_title', 'logo', 'title', 'description']
        widgets = {
            'org_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شعار البلاد أو الجهة'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان الاستبيان'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'وصف أو هدف الاستبيان'}),
        }

class NewQuestionForm(forms.ModelForm):
    choices = forms.CharField(
        label='الخيارات (كل خيار في سطر)',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'اكتب كل خيار في سطر منفصل', 'rows': 4}),
        help_text='اكتب كل خيار في سطر منفصل',
        required=True
    )
    class Meta:
        model = Question
        fields = ['question_text']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'نص السؤال', 'rows': 2}),
        }

    def clean_choices(self):
        data = self.cleaned_data['choices']
        choices = [c.strip() for c in data.split('\n') if c.strip()]
        if len(choices) < 2:
            raise forms.ValidationError('يجب إدخال خيارين على الأقل')
        return choices
