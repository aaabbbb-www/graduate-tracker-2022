from django.contrib import admin
from .models import Graduate, GraduateNote


@admin.register(Graduate)
class GraduateAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'student_id', 'graduation_year', 
        'college', 'major', 'employment_status', 'is_active'
    ]
    list_filter = [
        'graduation_year', 'college', 'major', 'employment_status', 
        'gender', 'degree', 'is_active'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'student_id', 
        'national_id', 'phone'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('المعلومات الشخصية', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone', 
                'national_id', 'gender', 'birth_date'
            )
        }),
        ('المعلومات الأكاديمية', {
            'fields': (
                'student_id', 'degree', 'major', 'college', 
                'graduation_year', 'gpa'
            )
        }),
        ('معلومات التوظيف', {
            'fields': (
                'employment_status', 'company_name', 'job_title', 
                'salary', 'work_start_date'
            )
        }),
        ('معلومات الاتصال', {
            'fields': ('address', 'city', 'country')
        }),
        ('معلومات النظام', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'الاسم الكامل'


@admin.register(GraduateNote)
class GraduateNoteAdmin(admin.ModelAdmin):
    list_display = ['graduate', 'created_by', 'created_at', 'note_preview']
    list_filter = ['created_at', 'created_by']
    search_fields = ['graduate__first_name', 'graduate__last_name', 'note']
    readonly_fields = ['created_at']
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'معاينة الملاحظة'

