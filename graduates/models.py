from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Graduate(models.Model):
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'موظف'),
        ('unemployed', 'غير موظف'),
        ('self_employed', 'عمل حر'),
        ('student', 'طالب'),
    ]
    
    DEGREE_CHOICES = [
        ('bachelor', 'بكالوريوس'),
        ('master', 'ماجستير'),
        ('phd', 'دكتوراه'),
        ('diploma', 'دبلوم'),
    ]

    # معلومات شخصية
    first_name = models.CharField(max_length=100, verbose_name='الاسم الأول')
    last_name = models.CharField(max_length=100, verbose_name='اسم العائلة')
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف', blank=True, null=True)
    national_id = models.CharField(max_length=20, unique=True, verbose_name='رقم الهوية', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='الجنس', blank=True, null=True)
    birth_date = models.DateField(verbose_name='تاريخ الميلاد', blank=True, null=True)
    
    # معلومات أكاديمية
    student_id = models.CharField(max_length=20, unique=True, verbose_name='الرقم الجامعي')
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES, verbose_name='الدرجة العلمية', blank=True, null=True)
    major = models.CharField(max_length=100, verbose_name='التخصص', blank=True, null=True)
    college = models.CharField(max_length=100, verbose_name='الكلية', blank=True, null=True)
    graduation_year = models.IntegerField(verbose_name='سنة التخرج', blank=True, null=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='المعدل التراكمي', blank=True, null=True)
    
    # معلومات التوظيف
    employment_status = models.CharField(
        max_length=20, 
        choices=EMPLOYMENT_STATUS_CHOICES, 
        verbose_name='حالة التوظيف',
        blank=True, null=True
    )
    company_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='اسم الشركة')
    job_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='المسمى الوظيفي')
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name='الراتب'
    )
    work_start_date = models.DateField(blank=True, null=True, verbose_name='تاريخ بداية العمل')
    
    # معلومات الاتصال
    address = models.TextField(verbose_name='العنوان', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='المدينة', blank=True, null=True)
    country = models.CharField(max_length=100, default='السعودية', verbose_name='الدولة', blank=True, null=True)
    
    # معلومات النظام
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        verbose_name = 'خريج'
        verbose_name_plural = 'الخريجون'
        ordering = ['-graduation_year', 'last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.graduation_year}"
    
    def get_absolute_url(self):
        return reverse('graduates:detail', kwargs={'pk': self.pk})
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


class GraduateNote(models.Model):
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField(verbose_name='الملاحظة')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='أنشئت بواسطة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'ملاحظة خريج'
        verbose_name_plural = 'ملاحظات الخريجين'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"ملاحظة على {self.graduate.full_name} - {self.created_at.date()}"

