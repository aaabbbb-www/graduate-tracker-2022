from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # الصفحة الرئيسية لإدارة التقارير
    path('', views.reports_home, name='home'),
    
    # التقارير الأساسية
    path('summary/', views.summary_report, name='summary'),
    path('employment/', views.employment_report, name='employment'),
    path('surveys/', views.survey_report, name='surveys'),
    
    # التقارير المخصصة
    path('custom/', views.custom_report, name='custom'),
    path('scheduled/', views.scheduled_reports, name='scheduled'),
    
    # التحليلات المتقدمة
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('graduates-analytics/', views.graduates_analytics, name='graduates_analytics'),
    
    # تصدير التقارير
    path('export/', views.export_reports, name='export'),
    path('export-options/', views.export_options, name='export_options'),
    path('bulk-export/', views.bulk_export, name='bulk_export'),
    
    # عرض التقارير المحفوظة
    path('<int:pk>/', views.view_report, name='view_report'),
    
    # APIs للرسوم البيانية
    path('api/employment-trends/', views.api_employment_trends, name='api_employment_trends'),
    path('api/survey-responses/', views.api_survey_responses_chart, name='api_survey_responses'),
    
    # تقرير شامل للخريجين
    path('graduates-summary/', views.graduates_summary, name='graduates_summary'),
    
    # المسارات الجديدة المضافة
    path('salary-analysis/', views.salary_analysis, name='salary_analysis'),
    path('response-analysis/', views.response_analysis, name='response_analysis'),
    path('interactive-dashboard/', views.interactive_dashboard, name='interactive_dashboard'),
    path('custom-charts/', views.custom_charts, name='custom_charts'),
    path('schedule-report/', views.schedule_report, name='schedule_report'),
    
    # تحليل جودة التعليم والبرامج الدراسية
    path('education-quality/', views.education_quality_analysis, name='education_quality_analysis'),

    # المسارات السريعة المطلوبة للقالب
    path('quick-summary/', views.quick_summary, name='quick_summary'),
    path('data-export/', views.data_export, name='data_export'),
    path('templates/', views.report_templates, name='templates'),
    path('settings/', views.report_settings, name='settings'),
]

