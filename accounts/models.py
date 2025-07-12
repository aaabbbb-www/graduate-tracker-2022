from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.utils import timezone

# نموذج ملف المستخدم الإضافي
class UserProfile(models.Model):
    """
    نموذج لتخزين معلومات إضافية عن المستخدم
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='المستخدم')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='رقم الهاتف')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='القسم')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='المنصب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    can_manage_graduates = models.BooleanField(default=False, verbose_name='إدارة الخريجين')
    can_manage_surveys = models.BooleanField(default=False, verbose_name='إدارة الاستبيانات')
    can_view_reports = models.BooleanField(default=False, verbose_name='عرض التقارير')
    # يمكن إضافة حقول أخرى حسب الحاجة

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"

# سجل الأنشطة للمستخدمين
class ActivityLog(models.Model):
    """
    نموذج لتسجيل أنشطة المستخدمين في النظام
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    action = models.CharField(max_length=255, verbose_name='الإجراء')
    details = models.TextField(blank=True, null=True, verbose_name='التفاصيل')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='التوقيت')
    user_agent = models.CharField(max_length=256, blank=True, null=True, verbose_name='وكيل المستخدم')

    class Meta:
        verbose_name = 'سجل النشاط'
        verbose_name_plural = 'سجلات النشاط'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

class Permission(models.Model):
    PERMISSION_CHOICES = [
        ('graduates_view', 'عرض الخريجين'),
        ('graduates_create', 'إضافة خريجين'),
        ('graduates_edit', 'تعديل الخريجين'),
        ('graduates_delete', 'حذف الخريجين'),
        ('graduates_export', 'تصدير بيانات الخريجين'),
        ('surveys_view', 'عرض الاستبيانات'),
        ('surveys_create', 'إنشاء استبيانات'),
        ('surveys_edit', 'تعديل الاستبيانات'),
        ('surveys_delete', 'حذف الاستبيانات'),
        ('surveys_responses', 'عرض إجابات الاستبيانات'),
        ('reports_view', 'عرض التقارير'),
        ('reports_create', 'إنشاء تقارير'),
        ('reports_export', 'تصدير التقارير'),
        ('users_manage', 'إدارة المستخدمين'),
        ('permissions_manage', 'إدارة الصلاحيات'),
        ('system_settings', 'إعدادات النظام'),
    ]
    
    name = models.CharField(max_length=100, choices=PERMISSION_CHOICES, unique=True, verbose_name='اسم الصلاحية')
    description = models.TextField(blank=True, null=True, verbose_name='وصف الصلاحية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'صلاحية'
        verbose_name_plural = 'الصلاحيات'
    
    def __str__(self):
        return self.get_name_display()

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم الدور')
    description = models.TextField(blank=True, null=True, verbose_name='وصف الدور')
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='الصلاحيات')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'دور'
        verbose_name_plural = 'الأدوار'
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('suspended', 'معلق'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', verbose_name='المستخدم')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='رقم الموظف')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الدور')
    department = models.CharField(max_length=100, verbose_name='القسم')
    position = models.CharField(max_length=100, verbose_name='المنصب')
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف')
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name='رقم الواتساب')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='الحالة')
    hire_date = models.DateField(verbose_name='تاريخ التعيين')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='المدير المباشر')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفون'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"
    
    def generate_password(self):
        """توليد كلمة مرور عشوائية"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(characters) for i in range(12))
        return password
    
    def send_credentials(self, password, method='email'):
        """إرسال بيانات الدخول للموظف"""
        if method == 'email':
            subject = 'بيانات الدخول - نظام تتبع الخريجين'
            message = f"""
            مرحباً {self.user.get_full_name()},
            
            تم إنشاء حسابك في نظام تتبع الخريجين.
            
            بيانات الدخول:
            اسم المستخدم: {self.user.username}
            كلمة المرور: {password}
            
            يرجى تغيير كلمة المرور بعد أول دخول.
            
            مع تحيات،
            فريق النظام
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.email],
                    fail_silently=False,
                )
                return True
            except Exception as e:
                print(f"خطأ في إرسال البريد الإلكتروني: {e}")
                return False
        
        elif method == 'whatsapp':
            # هنا يمكن إضافة كود لإرسال رسالة واتساب
            # يمكن استخدام API مثل Twilio أو WhatsApp Business API
            message = f"""
            مرحباً {self.user.get_full_name()},
            
            تم إنشاء حسابك في نظام تتبع الخريجين.
            
            بيانات الدخول:
            اسم المستخدم: {self.user.username}
            كلمة المرور: {password}
            
            يرجى تغيير كلمة المرور بعد أول دخول.
            """
            
            # TODO: إضافة كود إرسال الواتساب
            print(f"رسالة واتساب: {message}")
            return True
    
    def has_permission(self, permission_name):
        """التحقق من وجود صلاحية معينة"""
        if not self.role or not self.role.is_active:
            return False
        return self.role.permissions.filter(name=permission_name, is_active=True).exists()
    
    def get_all_permissions(self):
        """الحصول على جميع الصلاحيات"""
        if not self.role or not self.role.is_active:
            return []
        return self.role.permissions.filter(is_active=True)

class EmployeePermission(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='custom_permissions', verbose_name='الموظف')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name='الصلاحية')
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='منح بواسطة')
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ المنح')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ انتهاء الصلاحية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        verbose_name = 'صلاحية موظف'
        verbose_name_plural = 'صلاحيات الموظفين'
        unique_together = ['employee', 'permission']
    
    def __str__(self):
        return f"{self.employee} - {self.permission}"

class Notification(models.Model):
    """
    نموذج لإدارة الإشعارات في النظام
    """
    NOTIFICATION_TYPES = [
        ('info', 'معلومات'),
        ('success', 'نجاح'),
        ('warning', 'تحذير'),
        ('error', 'خطأ'),
        ('system', 'نظام'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='المستقبل')
    title = models.CharField(max_length=255, verbose_name='عنوان الإشعار')
    message = models.TextField(verbose_name='نص الإشعار')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name='نوع الإشعار')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ القراءة')
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_notification(cls, recipient, title, message, notification_type='info'):
        """إنشاء إشعار جديد"""
        return cls.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type
        )

class BackupLog(models.Model):
    """
    نموذج لتسجيل عمليات النسخ الاحتياطي
    """
    BACKUP_TYPES = [
        ('full', 'نسخة كاملة'),
        ('incremental', 'نسخة تدريجية'),
        ('manual', 'نسخة يدوية'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('running', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
    ]
    
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, verbose_name='نوع النسخة')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='مسار الملف')
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name='حجم الملف (بايت)')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ البدء')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الانتهاء')
    error_message = models.TextField(blank=True, null=True, verbose_name='رسالة الخطأ')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='أنشئ بواسطة')
    
    class Meta:
        verbose_name = 'سجل النسخ الاحتياطي'
        verbose_name_plural = 'سجلات النسخ الاحتياطي'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.get_backup_type_display()} - {self.get_status_display()} - {self.started_at}"
    
    @property
    def duration(self):
        """مدة النسخ الاحتياطي"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def file_size_mb(self):
        """حجم الملف بالميجابايت"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0 