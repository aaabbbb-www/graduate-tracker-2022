from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # الصفحة الرئيسية للاستبيانات الجديدة
    path('', views.new_surveys_home, name='home'),
    
    # إنشاء استبيان جديد
    path('create/', views.new_survey_create, name='create'),
    path('create/success/', views.new_survey_success, name='new_survey_success'),
    
    # عرض الاستبيان
    path('<int:pk>/', views.new_survey_detail, name='detail'),
    
    # عرض الاستبيان فقط (واجهة جمالية)
    path('<int:pk>/view/', views.view_survey, name='view'),
    
    # إضافة أسئلة للاستبيان
    path('<int:survey_pk>/add-question/', views.new_question_add, name='add_question'),
    path('<int:survey_pk>/question-added/', views.new_question_added, name='question_added'),
    
    # حذف سؤال
    path('<int:survey_pk>/delete-question/<int:question_pk>/', views.new_question_delete, name='delete_question'),
    
    # إرسال الاستبيان
    path('<int:pk>/send/', views.new_survey_send, name='send'),
    
    # أخذ الاستبيان (للخريجين)
    path('<int:pk>/take/', views.new_take_survey, name='take'),
    path('<int:pk>/submit/', views.new_submit_survey, name='submit'),
    path('<int:pk>/thank-you/', views.new_survey_thank_you, name='thank_you'),
    # قائمة الاستبيانات
    path('list/', views.new_survey_list, name='list'),
    # اختيار استبيان للتعديل
    path('edit-select/', views.edit_select, name='edit_select'),
    # اختيار استبيان للحذف
    path('delete-select/', views.delete_select, name='delete_select'),
    # اختيار استبيان للإرسال
    path('send-select/', views.send_select, name='send_select'),
    # تعديل استبيان
    path('<int:pk>/update/', views.survey_update, name='update'),
    # حذف استبيان
    path('<int:pk>/delete/', views.survey_delete, name='delete'),
    path('<int:pk>/send/', views.send_survey_select, name='send_survey_select'),
    path('take/<str:invitation_token>/', views.take_survey_by_token, name='take_survey_by_token'),
]

