from django import forms
from django.core.exceptions import ValidationError
from .models import Graduate, GraduateNote
from datetime import date


class GraduateForm(forms.ModelForm):
    class Meta:
        model = Graduate
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'national_id', 'gender',
            'birth_date', 'student_id', 'degree', 'major', 'college', 'graduation_year',
            'gpa', 'employment_status', 'company_name', 'job_title', 'salary',
            'work_start_date', 'address', 'city', 'country'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الاسم الأول'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم العائلة'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+966xxxxxxxxx'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهوية الوطنية'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرقم الجامعي'
            }),
            'degree': forms.Select(attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'التخصص'
            }),
            'college': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الكلية'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1990',
                'max': str(date.today().year + 5)
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '5'
            }),
            'employment_status': forms.Select(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الشركة'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المسمى الوظيفي'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'work_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان التفصيلي'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المدينة'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'السعودية'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اجعل جميع الحقول اختيارية ما عدا الاسم الأول واسم العائلة والرقم الجامعي
        required_fields = ['first_name', 'last_name', 'student_id']
        for field_name in self.fields:
            if field_name not in required_fields:
                self.fields[field_name].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Graduate.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('هذا البريد الإلكتروني مستخدم بالفعل')
        return email
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if national_id and Graduate.objects.filter(national_id=national_id).exclude(pk=self.instance.pk).exists():
            raise ValidationError('رقم الهوية هذا مستخدم بالفعل')
        return national_id
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id and Graduate.objects.filter(student_id=student_id).exclude(pk=self.instance.pk).exists():
            raise ValidationError('الرقم الجامعي هذا مستخدم بالفعل')
        return student_id
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if not birth_date:
            return birth_date  # إذا كان الحقل فارغ، أرجعه كما هو بدون تحقق
        if birth_date > date.today():
            raise ValidationError('تاريخ الميلاد لا يمكن أن يكون في المستقبل')
        age = date.today().year - birth_date.year
        if age < 16 or age > 80:
            raise ValidationError('العمر يجب أن يكون بين 16 و 80 سنة')
        return birth_date
    
    def clean_graduation_year(self):
        graduation_year = self.cleaned_data.get('graduation_year')
        if graduation_year is None or graduation_year == '':
            return graduation_year  # إذا كان الحقل فارغ، أرجعه كما هو بدون تحقق
        current_year = date.today().year
        if graduation_year < 1990 or graduation_year > current_year + 5:
            raise ValidationError(f'سنة التخرج يجب أن تكون بين 1990 و {current_year + 5}')
        return graduation_year
    
    def clean_gpa(self):
        gpa = self.cleaned_data.get('gpa')
        if gpa is None or gpa == '':
            return gpa  # إذا كان الحقل فارغ، أرجعه كما هو بدون تحقق
        if gpa < 0 or gpa > 5:
            raise ValidationError('المعدل التراكمي يجب أن يكون بين 0 و 5')
        return gpa


class GraduateSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث بالاسم، البريد الإلكتروني، أو الرقم الجامعي'
        })
    )
    
    graduation_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'سنة التخرج'
        })
    )
    
    college = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الكلية'
        })
    )
    
    major = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'التخصص'
        })
    )
    
    employment_status = forms.ChoiceField(
        choices=[('', 'جميع حالات التوظيف')] + Graduate.EMPLOYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class GraduateNoteForm(forms.ModelForm):
    class Meta:
        model = GraduateNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'أضف ملاحظة حول هذا الخريج...'
            })
        }


class GraduateImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text='يدعم ملفات Excel (.xlsx, .xls) و CSV'
    )
    
    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            if not file.name.endswith(('.xlsx', '.xls', '.csv')):
                raise ValidationError('نوع الملف غير مدعوم. يرجى رفع ملف Excel أو CSV')
            
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('حجم الملف كبير جداً. الحد الأقصى 5 ميجابايت')
        
        return file


class BulkActionForm(forms.Form):
    ACTION_CHOICES = [
        ('', 'اختر إجراء'),
        ('delete', 'حذف المحدد'),
        ('export', 'تصدير المحدد'),
        ('send_survey', 'إرسال استبيان'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    selected_graduates = forms.CharField(
        widget=forms.HiddenInput()
    )

