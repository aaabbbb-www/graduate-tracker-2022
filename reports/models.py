from django.db import models
from django.contrib.auth.models import User
from graduates.models import Graduate
from surveys.models import Survey


class Report(models.Model):
    REPORT_TYPES = [
        ('graduates_summary', 'ملخص الخريجين'),
        ('employment_status', 'حالة التوظيف'),
        ('survey_responses', 'استجابات الاستبيانات'),
        ('graduation_trends', 'اتجاهات التخرج'),
        ('salary_analysis', 'تحليل الرواتب'),
        ('geographic_distribution', 'التوزيع الجغرافي'),
        ('custom', 'تقرير مخصص'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان التقرير')
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPES,
        verbose_name='نوع التقرير'
    )
    description = models.TextField(blank=True, verbose_name='وصف التقرير')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='أنشئ بواسطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    # فلاتر التقرير
    filter_graduation_year_start = models.IntegerField(blank=True, null=True, verbose_name='سنة التخرج من')
    filter_graduation_year_end = models.IntegerField(blank=True, null=True, verbose_name='سنة التخرج إلى')
    filter_college = models.CharField(max_length=100, blank=True, verbose_name='الكلية')
    filter_major = models.CharField(max_length=100, blank=True, verbose_name='التخصص')
    filter_employment_status = models.CharField(max_length=20, blank=True, verbose_name='حالة التوظيف')
    filter_gender = models.CharField(max_length=10, blank=True, verbose_name='الجنس')
    filter_city = models.CharField(max_length=100, blank=True, verbose_name='المدينة')
    
    # إعدادات التقرير
    is_public = models.BooleanField(default=False, verbose_name='عام')
    auto_refresh = models.BooleanField(default=False, verbose_name='تحديث تلقائي')
    refresh_interval_days = models.IntegerField(default=7, verbose_name='فترة التحديث بالأيام')
    
    class Meta:
        verbose_name = 'تقرير'
        verbose_name_plural = 'التقارير'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ReportData(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='data')
    data_key = models.CharField(max_length=100, verbose_name='مفتاح البيانات')
    data_value = models.TextField(verbose_name='قيمة البيانات')
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('json', 'JSON'),
            ('text', 'نص'),
            ('number', 'رقم'),
            ('chart', 'رسم بياني'),
        ],
        default='json',
        verbose_name='نوع البيانات'
    )
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنتاج')
    
    class Meta:
        verbose_name = 'بيانات التقرير'
        verbose_name_plural = 'بيانات التقارير'
        unique_together = ['report', 'data_key']
    
    def __str__(self):
        return f"{self.report.title} - {self.data_key}"


class DashboardWidget(models.Model):
    WIDGET_TYPES = [
        ('counter', 'عداد'),
        ('chart', 'رسم بياني'),
        ('table', 'جدول'),
        ('progress', 'شريط تقدم'),
        ('list', 'قائمة'),
    ]
    
    title = models.CharField(max_length=100, verbose_name='عنوان الودجت')
    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPES,
        verbose_name='نوع الودجت'
    )
    description = models.TextField(blank=True, verbose_name='الوصف')
    query = models.TextField(verbose_name='الاستعلام')
    position_x = models.IntegerField(default=0, verbose_name='الموضع الأفقي')
    position_y = models.IntegerField(default=0, verbose_name='الموضع العمودي')
    width = models.IntegerField(default=4, verbose_name='العرض')
    height = models.IntegerField(default=3, verbose_name='الارتفاع')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    refresh_interval = models.IntegerField(default=300, verbose_name='فترة التحديث بالثواني')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='أنشئ بواسطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'ودجت لوحة التحكم'
        verbose_name_plural = 'ودجتات لوحة التحكم'
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return self.title


class ScheduledReport(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='schedules')
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        verbose_name='التكرار'
    )
    recipients = models.TextField(verbose_name='المستقبلون (بريد إلكتروني)')
    next_run = models.DateTimeField(verbose_name='التشغيل التالي')
    last_run = models.DateTimeField(blank=True, null=True, verbose_name='آخر تشغيل')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='أنشئ بواسطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تقرير مجدول'
        verbose_name_plural = 'التقارير المجدولة'
    
    def __str__(self):
        return f"{self.report.title} - {self.get_frequency_display()}"

