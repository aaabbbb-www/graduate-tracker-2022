from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, Employee, Role, Permission, EmployeePermission
import random
import string


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('هذا البريد الإلكتروني مستخدم بالفعل')
        return email


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone', 'department', 'position', 'is_active')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'description', 'permissions', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permissions': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeForm(forms.ModelForm):
    # حقول إضافية لإنشاء المستخدم
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    # خيارات إرسال بيانات الدخول
    SEND_METHOD_CHOICES = [
        ('email', 'البريد الإلكتروني'),
        ('whatsapp', 'الواتساب'),
        ('both', 'كليهما'),
        ('none', 'لا ترسل'),
    ]
    send_credentials = forms.ChoiceField(
        choices=SEND_METHOD_CHOICES,
        initial='email',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='طريقة إرسال بيانات الدخول'
    )
    
    class Meta:
        model = Employee
        fields = (
            'employee_id', 'role', 'department', 'position', 'phone', 'whatsapp',
            'status', 'hire_date', 'manager', 'notes'
        )
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديث قائمة المديرين لتشمل فقط الموظفين النشطين
        self.fields['manager'].queryset = Employee.objects.filter(status='active')
        
        # إذا كان هذا تعديل لموظف موجود
        if self.instance and self.instance.pk:
            if self.instance.user:
                self.fields['username'].initial = self.instance.user.username
                self.fields['first_name'].initial = self.instance.user.first_name
                self.fields['last_name'].initial = self.instance.user.last_name
                self.fields['email'].initial = self.instance.user.email
                # إخفاء حقول إنشاء المستخدم عند التعديل
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['send_credentials'].widget.attrs['disabled'] = True
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists() and not self.instance.pk:
            raise ValidationError('اسم المستخدم هذا مستخدم بالفعل')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() and not self.instance.pk:
            raise ValidationError('هذا البريد الإلكتروني مستخدم بالفعل')
        return email
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists() and not self.instance.pk:
            raise ValidationError('رقم الموظف هذا مستخدم بالفعل')
        return employee_id


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            'role', 'department', 'position', 'phone', 'whatsapp',
            'status', 'manager', 'notes'
        )
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = Employee.objects.filter(status='active')


class EmployeePermissionForm(forms.ModelForm):
    class Meta:
        model = EmployeePermission
        fields = ('permission', 'expires_at', 'is_active')
        widgets = {
            'permission': forms.Select(attrs={'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BulkPermissionForm(forms.Form):
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(status='active'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='الموظفون'
    )
    
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='الصلاحيات'
    )
    
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label='تاريخ انتهاء الصلاحية (اختياري)'
    )


class EmployeeSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث بالاسم أو رقم الموظف'
        })
    )
    
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'القسم'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + Employee.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        required=False,
        empty_label="جميع الأدوار",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class PasswordResetForm(forms.Form):
    SEND_METHOD_CHOICES = [
        ('email', 'البريد الإلكتروني'),
        ('whatsapp', 'الواتساب'),
        ('both', 'كليهما'),
    ]
    
    send_method = forms.ChoiceField(
        choices=SEND_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='طريقة الإرسال'
    )
    
    def __init__(self, employee, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee = employee


class UserPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='كلمة المرور الحالية'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='كلمة المرور الجديدة'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='تأكيد كلمة المرور الجديدة'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError('كلمتا المرور غير متطابقتين')
        
        return cleaned_data
