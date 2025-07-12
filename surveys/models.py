from django.db import models
from django.contrib.auth.models import User
from graduates.models import Graduate
from django.urls import reverse


class Survey(models.Model):
    SURVEY_STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('active', 'نشط'),
        ('closed', 'مغلق'),
    ]
    
    SEND_METHOD_CHOICES = [
        ('email', 'بريد إلكتروني'),
        ('whatsapp', 'واتساب'),
        ('both', 'كليهما'),
    ]
    
    SURVEY_TYPE_CHOICES = [
        ('template', 'من قالب جاهز'),
        ('google_forms', 'Google Forms'),
        ('custom', 'مخصص'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان الاستبيان')
    description = models.TextField(verbose_name='وصف الاستبيان')
    status = models.CharField(
        max_length=10, 
        choices=SURVEY_STATUS_CHOICES, 
        default='draft',
        verbose_name='حالة الاستبيان'
    )
    survey_type = models.CharField(
        max_length=20,
        choices=SURVEY_TYPE_CHOICES,
        default='custom',
        verbose_name='نوع الاستبيان'
    )
    template_name = models.CharField(max_length=100, blank=True, verbose_name='اسم القالب')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='أنشئ بواسطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    start_date = models.DateTimeField(verbose_name='تاريخ البداية')
    end_date = models.DateTimeField(verbose_name='تاريخ النهاية')
    google_form_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='رابط جوجل فورم')
    org_title = models.CharField(max_length=255, blank=True, null=True, verbose_name='عنوان الجهة')
    logo = models.ImageField(upload_to='survey_logos/', blank=True, null=True, verbose_name='شعار الجهة')
    
    # حقول إرسال الاستبيان
    send_method = models.CharField(
        max_length=10,
        choices=SEND_METHOD_CHOICES,
        default='email',
        verbose_name='طريقة الإرسال'
    )
    auto_send = models.BooleanField(default=False, verbose_name='إرسال تلقائي بعد الإنشاء')
    email_subject = models.CharField(max_length=200, blank=True, verbose_name='موضوع البريد الإلكتروني')
    email_message = models.TextField(blank=True, verbose_name='رسالة البريد الإلكتروني')
    whatsapp_message = models.TextField(blank=True, verbose_name='رسالة الواتساب')
    
    # إحصائيات الإرسال
    total_sent = models.IntegerField(default=0, verbose_name='إجمالي المرسل إليهم')
    email_sent = models.IntegerField(default=0, verbose_name='عدد رسائل البريد المرسلة')
    whatsapp_sent = models.IntegerField(default=0, verbose_name='عدد رسائل الواتساب المرسلة')
    responses_received = models.IntegerField(default=0, verbose_name='عدد الاستجابات المستلمة')
    
    class Meta:
        verbose_name = 'استبيان'
        verbose_name_plural = 'الاستبيانات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} (ID: {self.id})"
    
    def get_absolute_url(self):
        return reverse('surveys:detail', kwargs={'pk': self.pk})
    
    def get_email_subject(self):
        """الحصول على موضوع البريد الإلكتروني"""
        if self.email_subject:
            return self.email_subject
        return f'استبيان: {self.title}'
    
    def get_email_message(self, graduate):
        """الحصول على رسالة البريد الإلكتروني"""
        survey_url = f'http://127.0.0.1:8000/surveys/{self.pk}/take-public/'
        
        if self.email_message:
            return self.email_message.replace('{survey_url}', survey_url)
        
        return f'''
        عزيزي/عزيزتي {graduate.full_name}،
        
        نرجو منك المشاركة في الاستبيان التالي:

        عنوان الاستبيان: {self.title}
        وصف الاستبيان: {self.description}
        
        للمشاركة، يرجى النقر على الرابط التالي:
        {survey_url}
        
        تاريخ انتهاء الاستبيان: {self.end_date.strftime('%Y-%m-%d')}
        
        ملاحظات مهمة:
        - يمكنك الإجابة على الاستبيان مرة واحدة فقط
        - سيتم حفظ إجاباتك بشكل آمن ومجهول
        - البيانات ستستخدم لأغراض بحثية وتحليلية فقط
        
        شكراً لك على وقتك ومشاركتك.
        
        مع تحيات،
        فريق إدارة الخريجين
        '''
    
    def get_whatsapp_message(self, graduate):
        """الحصول على رسالة الواتساب"""
        survey_url = f'http://127.0.0.1:8000/surveys/{self.pk}/take-public/'
        
        if self.whatsapp_message:
            return self.whatsapp_message.replace('{survey_url}', survey_url)
        
        return f'''مرحباً {graduate.full_name}،

نرجو مشاركتك في استبيان: {self.title}

{self.description}

رابط الاستبيان: {survey_url}

ينتهي في: {self.end_date.strftime('%Y-%m-%d')}

ملاحظات:
• إجابة واحدة فقط
• بيانات آمنة ومجهولة
• لأغراض بحثية فقط

شكراً لك!'''
    
    def get_response_rate(self):
        """حساب معدل الاستجابة"""
        if self.total_sent > 0:
            return round((self.responses_received / self.total_sent) * 100, 1)
        return 0


class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'نص'),
        ('textarea', 'نص طويل'),
        ('radio', 'اختيار من متعدد'),
        ('checkbox', 'اختيار متعدد'),
        ('select', 'قائمة منسدلة'),
        ('number', 'رقم'),
        ('email', 'بريد إلكتروني'),
        ('date', 'تاريخ'),
        ('rating', 'تقييم'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(verbose_name='نص السؤال')
    question_type = models.CharField(
        max_length=20, 
        choices=QUESTION_TYPES,
        verbose_name='نوع السؤال'
    )
    is_required = models.BooleanField(default=False, verbose_name='مطلوب')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    help_text = models.CharField(max_length=200, blank=True, verbose_name='نص المساعدة')
    
    class Meta:
        verbose_name = 'سؤال'
        verbose_name_plural = 'الأسئلة'
        ordering = ['survey', 'order']
    
    def __str__(self):
        return f"{self.survey.title} - {self.question_text[:50]}"


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200, verbose_name='نص الخيار')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    
    class Meta:
        verbose_name = 'خيار السؤال'
        verbose_name_plural = 'خيارات الأسئلة'
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]} - {self.choice_text}"


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='survey_responses')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')
    is_complete = models.BooleanField(default=False, verbose_name='مكتمل')
    
    class Meta:
        verbose_name = 'استجابة الاستبيان'
        verbose_name_plural = 'استجابات الاستبيانات'
        unique_together = ['survey', 'graduate']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.graduate.full_name} - {self.survey.title}"


class Answer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, verbose_name='إجابة نصية')
    answer_number = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name='إجابة رقمية'
    )
    answer_date = models.DateField(blank=True, null=True, verbose_name='إجابة تاريخ')
    selected_choices = models.ManyToManyField(
        QuestionChoice, 
        blank=True,
        verbose_name='الخيارات المحددة'
    )
    
    class Meta:
        verbose_name = 'إجابة'
        verbose_name_plural = 'الإجابات'
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"{self.response.graduate.full_name} - {self.question.question_text[:30]}"


class SurveyInvitation(models.Model):
    """دعوة استبيان"""
    INVITATION_STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('sent', 'تم الإرسال'),
        ('opened', 'تم الفتح'),
        ('completed', 'تم الإكمال'),
        ('failed', 'فشل'),
    ]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='invitations')
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='survey_invitations')
    invitation_token = models.CharField(max_length=100, unique=True, verbose_name='الرمز المميز')
    status = models.CharField(
        max_length=20,
        choices=INVITATION_STATUS_CHOICES,
        default='pending',
        verbose_name='حالة الدعوة'
    )
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإرسال')
    opened_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الفتح')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإكمال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'دعوة استبيان'
        verbose_name_plural = 'دعوات الاستبيانات'
        unique_together = ['survey', 'graduate']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"دعوة {self.graduate.full_name} لـ {self.survey.title}"


class SurveySendLog(models.Model):
    """سجل إرسال الاستبيانات"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='send_logs')
    graduate = models.ForeignKey('graduates.Graduate', on_delete=models.CASCADE)
    send_method = models.CharField(max_length=10, choices=Survey.SEND_METHOD_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent', choices=[
        ('sent', 'تم الإرسال'),
        ('failed', 'فشل الإرسال'),
        ('delivered', 'تم التسليم'),
        ('read', 'تم القراءة'),
    ])
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'سجل إرسال استبيان'
        verbose_name_plural = 'سجلات إرسال الاستبيانات'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.survey.title} - {self.graduate.full_name} - {self.send_method}"


class SurveyTemplate(models.Model):
    """
    نموذج لقالب الاستبيان لتخزين قوالب الأسئلة الجاهزة
    """
    title = models.CharField(max_length=200, verbose_name='عنوان القالب')
    description = models.TextField(verbose_name='وصف القالب')
    category = models.CharField(max_length=100, default='عام', verbose_name='الفئة')
    difficulty = models.CharField(max_length=50, default='متوسط', verbose_name='الصعوبة')
    is_public = models.BooleanField(default=False, verbose_name='عام')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='أنشئ بواسطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'قالب استبيان'
        verbose_name_plural = 'قوالب الاستبيانات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Graduate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    full_name = models.CharField(max_length=100, verbose_name='الاسم الكامل')
    email = models.EmailField(max_length=254, verbose_name='البريد الإلكتروني')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    graduation_year = models.IntegerField(blank=True, null=True, verbose_name='سنة التخرج')
    token = models.CharField(max_length=100, unique=True, verbose_name='الرمز المميز')
    degree = models.CharField(max_length=100, blank=True, verbose_name='الدرجة العلمية')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    target_college = models.CharField(max_length=100, blank=True, null=True, verbose_name='الكلية المستهدفة')

    class Meta:
        verbose_name = 'خريج'
        verbose_name_plural = 'خريجون'
        ordering = ['-graduation_year', 'full_name']

    def __str__(self):
        return self.full_name
