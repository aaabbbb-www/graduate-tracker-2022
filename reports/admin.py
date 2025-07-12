from django.contrib import admin
from .models import Report, ReportData, DashboardWidget, ScheduledReport


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'created_by', 'is_public', 'auto_refresh', 'created_at']
    list_filter = ['report_type', 'is_public', 'auto_refresh', 'created_by', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات التقرير', {
            'fields': ('title', 'report_type', 'description', 'created_by')
        }),
        ('فلاتر التقرير', {
            'fields': (
                'filter_graduation_year_start', 'filter_graduation_year_end',
                'filter_college', 'filter_major', 'filter_employment_status',
                'filter_gender', 'filter_city'
            ),
            'classes': ('collapse',)
        }),
        ('إعدادات التقرير', {
            'fields': ('is_public', 'auto_refresh', 'refresh_interval_days')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    list_display = ['report', 'data_key', 'data_type', 'generated_at']
    list_filter = ['data_type', 'generated_at', 'report__report_type']
    search_fields = ['report__title', 'data_key']
    readonly_fields = ['generated_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'widget_type', 'position_x', 'position_y', 'is_active', 'created_by']
    list_filter = ['widget_type', 'is_active', 'created_by']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('معلومات الودجت', {
            'fields': ('title', 'widget_type', 'description', 'query')
        }),
        ('الموضع والحجم', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('الإعدادات', {
            'fields': ('is_active', 'refresh_interval', 'created_by')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['report', 'frequency', 'next_run', 'last_run', 'is_active', 'created_by']
    list_filter = ['frequency', 'is_active', 'created_by']
    search_fields = ['report__title', 'recipients']
    readonly_fields = ['last_run', 'created_at']
    
    fieldsets = (
        ('معلومات الجدولة', {
            'fields': ('report', 'frequency', 'recipients')
        }),
        ('التوقيت', {
            'fields': ('next_run', 'last_run')
        }),
        ('الإعدادات', {
            'fields': ('is_active', 'created_by')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

