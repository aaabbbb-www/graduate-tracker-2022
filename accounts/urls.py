from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # تسجيل الدخول والخروج
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='signup'),
    
    # الصفحة الرئيسية لإدارة الحسابات
    path('', views.accounts_home, name='home'),
    
    # إدارة المستخدمين
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # الملف الشخصي
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # إدارة الموظفين
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/<int:pk>/permissions/', views.employee_permissions, name='employee_permissions'),
    path('employees/<int:pk>/reset-password/', views.reset_employee_password, name='reset_employee_password'),
    
    # إدارة الأدوار
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/edit/', views.role_update, name='role_update'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    
    # إدارة الصلاحيات
    path('permissions/', views.permission_list, name='permission_list'),
    path('permissions/bulk/', views.bulk_permissions, name='bulk_permissions'),
    path('permissions/<int:pk>/remove/', views.remove_permission, name='remove_permission'),
    
    # إدارة الصلاحيات (القديمة)
    path('permissions-management/', views.permissions_management, name='permissions_management'),
    
    # سجل الأنشطة
    path('activity/', views.activity_log, name='activity'),
    
    # إعدادات النظام
    path('settings/', views.system_settings, name='settings'),
    
    # APIs
    path('api/user-activity/', views.api_user_activity_chart, name='api_user_activity'),
    path('api/user-stats/', views.api_user_stats, name='api_user_stats'),
    path('api/employee-stats/', views.api_employee_stats, name='api_employee_stats'),
    path('api/permission-stats/', views.api_permission_stats, name='api_permission_stats'),
    
    # الإشعارات
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notification-stats/', views.api_notification_stats, name='api_notification_stats'),
    
    # النسخ الاحتياطي
    path('backups/', views.backup_list, name='backup_list'),
    path('backups/create/', views.create_backup, name='create_backup'),
    path('backups/<int:pk>/', views.backup_detail, name='backup_detail'),
]

