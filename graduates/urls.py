from django.urls import path
from . import views

app_name = 'graduates'

urlpatterns = [
    # الصفحة الرئيسية لإدارة الخريجين
    path('', views.graduates_home, name='home'),
    
    # إدارة الخريجين
    path('list/', views.graduate_list, name='list'),
    path('create/', views.graduate_create, name='create'),
    path('<int:pk>/', views.graduate_detail, name='detail'),
    path('<int:pk>/edit/', views.graduate_update, name='update'),
    path('<int:pk>/delete/', views.graduate_delete, name='delete'),
    
    # البحث والفلترة
    path('search/', views.graduate_search, name='search'),
    
    # الإحصائيات والتحليلات
    path('statistics/', views.employment_statistics, name='statistics'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    
    # استيراد وتصدير البيانات
    path('import-export/', views.import_export, name='import_export'),
    
    # APIs للرسوم البيانية
    path('api/employment-chart/', views.api_employment_chart_data, name='api_employment_chart'),
]

