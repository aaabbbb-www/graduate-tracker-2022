from django import forms
from .models import Report, DashboardWidget
from graduates.models import Graduate


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'title', 'report_type', 'description', 'filter_graduation_year_start',
            'filter_graduation_year_end', 'filter_college', 'filter_major',
            'filter_employment_status', 'filter_gender', 'filter_city',
            'is_public', 'auto_refresh', 'refresh_interval_days'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان التقرير'
            }),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'وصف التقرير'
            }),
            'filter_graduation_year_start': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'من سنة'
            }),
            'filter_graduation_year_end': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'إلى سنة'
            }),
            'filter_college': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الكلية'
            }),
            'filter_major': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'التخصص'
            }),
            'filter_employment_status': forms.Select(attrs={'class': 'form-control'}),
            'filter_gender': forms.Select(attrs={'class': 'form-control'}),
            'filter_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المدينة'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_refresh': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'refresh_interval_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة خيارات فارغة للفلاتر الاختيارية
        self.fields['filter_employment_status'].choices = [('', 'جميع الحالات')] + Graduate.EMPLOYMENT_STATUS_CHOICES
        self.fields['filter_gender'].choices = [('', 'الجميع')] + Graduate.GENDER_CHOICES


class DashboardWidgetForm(forms.ModelForm):
    class Meta:
        model = DashboardWidget
        fields = [
            'title', 'widget_type', 'description', 'query',
            'position_x', 'position_y', 'width', 'height',
            'refresh_interval', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان الودجت'
            }),
            'widget_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الودجت'
            }),
            'query': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'استعلام البيانات'
            }),
            'position_x': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'position_y': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '12'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'refresh_interval': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '30'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReportFilterForm(forms.Form):
    REPORT_TYPE_CHOICES = [('', 'جميع الأنواع')] + Report.REPORT_TYPES
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
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
        empty_label='جميع المنشئين',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        self.fields['created_by'].queryset = User.objects.filter(
            report_set__isnull=False
        ).distinct()


class QuickStatsForm(forms.Form):
    """نموذج لعرض إحصائيات سريعة"""
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
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

