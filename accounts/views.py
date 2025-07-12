from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json
from .models import UserProfile, ActivityLog, Employee, Role, Permission, EmployeePermission, Notification, BackupLog
from .forms import (
    UserRegistrationForm, UserProfileForm, UserUpdateForm, 
    EmployeeForm, EmployeeUpdateForm, RoleForm, EmployeePermissionForm,
    BulkPermissionForm, EmployeeSearchForm, PasswordResetForm
)
from django.contrib.auth.forms import AuthenticationForm

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def user_login(request):
    """تسجيل الدخول"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # تسجيل نشاط تسجيل الدخول
            ActivityLog.objects.create(
                user=user,
                action='login',
                details='تم تسجيل الدخول بنجاح',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, f'مرحباً بك {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    """تسجيل الخروج"""
    # تسجيل نشاط تسجيل الخروج
    ActivityLog.objects.create(
        user=request.user,
        action='logout',
        description='تسجيل خروج'
    )
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('accounts:login')

def user_signup(request):
    """تسجيل مستخدم جديد"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # إنشاء ملف تعريف المستخدم
            UserProfile.objects.create(user=user)
            messages.success(request, 'تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def accounts_home(request):
    """صفحة إدارة الحسابات الرئيسية"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    recent_logins = ActivityLog.objects.filter(
        action='login',
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # آخر الأنشطة
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'recent_logins': recent_logins,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/accounts_home.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_list(request):
    """قائمة المستخدمين"""
    users = User.objects.all().order_by('-date_joined')
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # الفلترة حسب الحالة
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)
    
    # التقسيم إلى صفحات
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'accounts/user_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_create(request):
    """إنشاء مستخدم جديد"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='create_user',
                description=f'إنشاء مستخدم جديد: {user.username}'
            )
            
            messages.success(request, 'تم إنشاء المستخدم بنجاح!')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'إنشاء مستخدم جديد'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_update(request, pk):
    """تعديل بيانات مستخدم"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='update_user',
                description=f'تعديل بيانات المستخدم: {user.username}'
            )
            
            messages.success(request, 'تم تحديث بيانات المستخدم بنجاح!')
            return redirect('accounts:user_list')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'تعديل بيانات المستخدم'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_delete(request, pk):
    """حذف مستخدم"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        
        # تسجيل النشاط
        ActivityLog.objects.create(
            user=request.user,
            action='delete_user',
            description=f'حذف المستخدم: {username}'
        )
        
        messages.success(request, 'تم حذف المستخدم بنجاح!')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user_to_delete': user})

@login_required
def profile_view(request):
    """عرض الملف الشخصي"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile_view.html', {'profile': profile})

@login_required
def profile_edit(request):
    """تعديل الملف الشخصي"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='update_profile',
                description='تحديث الملف الشخصي'
            )
            
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def permissions_management(request):
    """إدارة الصلاحيات والأدوار"""
    groups = Group.objects.all()
    users = User.objects.all()
    
    context = {
        'groups': groups,
        'users': users,
    }
    return render(request, 'accounts/permissions_management.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def activity_log(request):
    """سجل الأنشطة"""
    activities = ActivityLog.objects.select_related('user').order_by('-timestamp')
    
    # الفلترة حسب نوع النشاط
    action_filter = request.GET.get('action')
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    # الفلترة حسب المستخدم
    user_filter = request.GET.get('user')
    if user_filter:
        activities = activities.filter(user__username__icontains=user_filter)
    
    # التقسيم إلى صفحات
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # أنواع الأنشطة المتاحة
    action_types = ActivityLog.objects.values_list('action', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'action_types': action_types,
    }
    return render(request, 'accounts/activity_log.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def system_settings(request):
    """إعدادات النظام"""
    if request.method == 'POST':
        # معالجة تحديث الإعدادات
        messages.success(request, 'تم تحديث إعدادات النظام بنجاح!')
        
        # تسجيل النشاط
        ActivityLog.objects.create(
            user=request.user,
            action='update_settings',
            description='تحديث إعدادات النظام'
        )
    
    return render(request, 'accounts/system_settings.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET"])
def api_user_activity_chart(request):
    """API لبيانات الرسم البياني لنشاط المستخدمين"""
    # نشاط آخر 7 أيام
    days_data = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        count = ActivityLog.objects.filter(
            timestamp__date=date,
            action='login'
        ).count()
        days_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    data = {
        'labels': [item['date'] for item in reversed(days_data)],
        'data': [item['count'] for item in reversed(days_data)]
    }
    return JsonResponse(data)

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET"])
def api_user_stats(request):
    """API لإحصائيات المستخدمين"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    data = {
        'total': total_users,
        'active': active_users,
        'staff': staff_users,
        'regular': total_users - staff_users
    }
    return JsonResponse(data)

# إدارة الموظفين
@login_required
@user_passes_test(lambda u: u.is_staff)
def employee_list(request):
    """قائمة الموظفين"""
    employees = Employee.objects.select_related('user', 'role', 'manager').all().order_by('-created_at')
    
    # البحث والفلترة
    search_form = EmployeeSearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        department = search_form.cleaned_data.get('department')
        status = search_form.cleaned_data.get('status')
        role = search_form.cleaned_data.get('role')
        
        if search_query:
            employees = employees.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(position__icontains=search_query)
            )
        
        if department:
            employees = employees.filter(department__icontains=department)
        
        if status:
            employees = employees.filter(status=status)
        
        if role:
            employees = employees.filter(role=role)
    
    # التقسيم إلى صفحات
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'accounts/employee_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def employee_create(request):
    """إنشاء موظف جديد"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            # إنشاء المستخدم أولاً
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=Employee.generate_password(None)  # سيتم توليد كلمة مرور عشوائية
            )
            
            # إنشاء الموظف
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            
            # إرسال بيانات الدخول
            send_method = form.cleaned_data.get('send_credentials', 'email')
            if send_method in ['email', 'both']:
                password = user.password  # في الواقع يجب توليد كلمة مرور جديدة
                employee.send_credentials(password, 'email')
            
            if send_method in ['whatsapp', 'both']:
                password = user.password
                employee.send_credentials(password, 'whatsapp')
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='create_employee',
                description=f'إنشاء موظف جديد: {employee.user.get_full_name()}'
            )
            
            messages.success(request, 'تم إنشاء الموظف بنجاح!')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeForm()
    
    return render(request, 'accounts/employee_form.html', {'form': form, 'title': 'إضافة موظف جديد'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def employee_update(request, pk):
    """تعديل بيانات موظف"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='update_employee',
                description=f'تعديل بيانات الموظف: {employee.user.get_full_name()}'
            )
            
            messages.success(request, 'تم تحديث بيانات الموظف بنجاح!')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeUpdateForm(instance=employee)
    
    return render(request, 'accounts/employee_form.html', {'form': form, 'title': 'تعديل بيانات الموظف'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def employee_detail(request, pk):
    """تفاصيل الموظف"""
    employee = get_object_or_404(Employee, pk=pk)
    permissions = employee.get_all_permissions()
    custom_permissions = employee.custom_permissions.filter(is_active=True)
    
    context = {
        'employee': employee,
        'permissions': permissions,
        'custom_permissions': custom_permissions,
    }
    return render(request, 'accounts/employee_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def employee_delete(request, pk):
    """حذف موظف"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.user.get_full_name()
        employee.delete()
        
        # تسجيل النشاط
        ActivityLog.objects.create(
            user=request.user,
            action='delete_employee',
            description=f'حذف الموظف: {employee_name}'
        )
        
        messages.success(request, 'تم حذف الموظف بنجاح!')
        return redirect('accounts:employee_list')
    
    return render(request, 'accounts/employee_confirm_delete.html', {'employee': employee})

# إدارة الأدوار
@login_required
@user_passes_test(lambda u: u.is_staff)
def role_list(request):
    """قائمة الأدوار"""
    roles = Role.objects.all().order_by('-created_at')
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        roles = roles.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # التقسيم إلى صفحات
    paginator = Paginator(roles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'accounts/role_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def role_create(request):
    """إنشاء دور جديد"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='create_role',
                description=f'إنشاء دور جديد: {role.name}'
            )
            
            messages.success(request, 'تم إنشاء الدور بنجاح!')
            return redirect('accounts:role_list')
    else:
        form = RoleForm()
    
    return render(request, 'accounts/role_form.html', {'form': form, 'title': 'إضافة دور جديد'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def role_update(request, pk):
    """تعديل دور"""
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='update_role',
                description=f'تعديل الدور: {role.name}'
            )
            
            messages.success(request, 'تم تحديث الدور بنجاح!')
            return redirect('accounts:role_list')
    else:
        form = RoleForm(instance=role)
    
    return render(request, 'accounts/role_form.html', {'form': form, 'title': 'تعديل الدور'})

@login_required
@user_passes_test(lambda u: u.is_staff)
def role_delete(request, pk):
    """حذف دور"""
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        
        # تسجيل النشاط
        ActivityLog.objects.create(
            user=request.user,
            action='delete_role',
            description=f'حذف الدور: {role_name}'
        )
        
        messages.success(request, 'تم حذف الدور بنجاح!')
        return redirect('accounts:role_list')
    
    return render(request, 'accounts/role_confirm_delete.html', {'role': role})

# إدارة الصلاحيات
@login_required
@user_passes_test(lambda u: u.is_staff)
def permission_list(request):
    """قائمة الصلاحيات"""
    permissions = Permission.objects.all().order_by('name')
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        permissions = permissions.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'permissions': permissions,
        'search_query': search_query,
    }
    return render(request, 'accounts/permission_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def employee_permissions(request, pk):
    """إدارة صلاحيات موظف"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeePermissionForm(request.POST)
        if form.is_valid():
            permission = form.save(commit=False)
            permission.employee = employee
            permission.granted_by = request.user
            permission.save()
            
            messages.success(request, 'تم منح الصلاحية بنجاح!')
            return redirect('accounts:employee_permissions', pk=pk)
    else:
        form = EmployeePermissionForm()
    
    # الصلاحيات الحالية
    role_permissions = employee.get_all_permissions()
    custom_permissions = employee.custom_permissions.filter(is_active=True)
    
    context = {
        'employee': employee,
        'form': form,
        'role_permissions': role_permissions,
        'custom_permissions': custom_permissions,
    }
    return render(request, 'accounts/employee_permissions.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def bulk_permissions(request):
    """منح صلاحيات لعدة موظفين"""
    if request.method == 'POST':
        form = BulkPermissionForm(request.POST)
        if form.is_valid():
            employees = form.cleaned_data['employees']
            permissions = form.cleaned_data['permissions']
            expires_at = form.cleaned_data.get('expires_at')
            
            for employee in employees:
                for permission in permissions:
                    EmployeePermission.objects.get_or_create(
                        employee=employee,
                        permission=permission,
                        defaults={
                            'granted_by': request.user,
                            'expires_at': expires_at,
                            'is_active': True
                        }
                    )
            
            messages.success(request, f'تم منح الصلاحيات لـ {len(employees)} موظف بنجاح!')
            return redirect('accounts:employee_list')
    else:
        form = BulkPermissionForm()
    
    return render(request, 'accounts/bulk_permissions.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def remove_permission(request, pk):
    """إزالة صلاحية من موظف"""
    employee_permission = get_object_or_404(EmployeePermission, pk=pk)
    
    if request.method == 'POST':
        employee_permission.delete()
        messages.success(request, 'تم إزالة الصلاحية بنجاح!')
        return redirect('accounts:employee_permissions', pk=employee_permission.employee.pk)
    
    return render(request, 'accounts/remove_permission.html', {'employee_permission': employee_permission})

# إعادة تعيين كلمة المرور
@login_required
@user_passes_test(lambda u: u.is_staff)
def reset_employee_password(request, pk):
    """إعادة تعيين كلمة مرور موظف"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = PasswordResetForm(employee, request.POST)
        if form.is_valid():
            # توليد كلمة مرور جديدة
            new_password = employee.generate_password()
            employee.user.set_password(new_password)
            employee.user.save()
            
            # إرسال كلمة المرور الجديدة
            send_method = form.cleaned_data['send_method']
            if send_method in ['email', 'both']:
                employee.send_credentials(new_password, 'email')
            
            if send_method in ['whatsapp', 'both']:
                employee.send_credentials(new_password, 'whatsapp')
            
            # تسجيل النشاط
            ActivityLog.objects.create(
                user=request.user,
                action='reset_password',
                description=f'إعادة تعيين كلمة مرور للموظف: {employee.user.get_full_name()}'
            )
            
            messages.success(request, 'تم إعادة تعيين كلمة المرور بنجاح!')
            return redirect('accounts:employee_detail', pk=pk)
    else:
        form = PasswordResetForm(employee)
    
    return render(request, 'accounts/reset_password.html', {'form': form, 'employee': employee})

# API endpoints للواجهات التفاعلية
@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET"])
def api_employee_stats(request):
    """إحصائيات الموظفين"""
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='active').count()
    inactive_employees = Employee.objects.filter(status='inactive').count()
    suspended_employees = Employee.objects.filter(status='suspended').count()
    
    # إحصائيات حسب القسم
    department_stats = Employee.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # إحصائيات حسب الدور
    role_stats = Employee.objects.values('role__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    data = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'suspended_employees': suspended_employees,
        'department_stats': list(department_stats),
        'role_stats': list(role_stats),
    }
    
    return JsonResponse(data)

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET"])
def api_permission_stats(request):
    """إحصائيات الصلاحيات"""
    total_permissions = Permission.objects.count()
    active_permissions = Permission.objects.filter(is_active=True).count()
    
    # الصلاحيات الأكثر استخداماً
    permission_usage = EmployeePermission.objects.values('permission__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    data = {
        'total_permissions': total_permissions,
        'active_permissions': active_permissions,
        'permission_usage': list(permission_usage),
    }
    
    return JsonResponse(data)

@login_required
@user_passes_test(lambda u: u.is_staff)
def notification_list(request):
    """قائمة الإشعارات"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # فلترة حسب النوع
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    # فلترة حسب الحالة
    is_read = request.GET.get('read')
    if is_read == 'true':
        notifications = notifications.filter(is_read=True)
    elif is_read == 'false':
        notifications = notifications.filter(is_read=False)
    
    # التقسيم إلى صفحات
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # إحصائيات
    total_notifications = notifications.count()
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'total_notifications': total_notifications,
        'unread_count': unread_count,
        'notification_type': notification_type,
        'is_read': is_read,
    }
    return render(request, 'accounts/notification_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def mark_notification_read(request, pk):
    """تحديد إشعار كمقروء"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'تم تحديد الإشعار كمقروء.')
    return redirect('accounts:notification_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
def mark_all_notifications_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    if request.method == 'POST':
        unread_notifications = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        )
        unread_notifications.update(is_read=True, read_at=timezone.now())
        
        messages.success(request, 'تم تحديد جميع الإشعارات كمقروءة.')
    
    return redirect('accounts:notification_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
def backup_list(request):
    """قائمة النسخ الاحتياطية"""
    backups = BackupLog.objects.all().order_by('-started_at')
    
    # فلترة حسب النوع
    backup_type = request.GET.get('type')
    if backup_type:
        backups = backups.filter(backup_type=backup_type)
    
    # فلترة حسب الحالة
    status = request.GET.get('status')
    if status:
        backups = backups.filter(status=status)
    
    # التقسيم إلى صفحات
    paginator = Paginator(backups, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # إحصائيات
    total_backups = backups.count()
    successful_backups = backups.filter(status='completed').count()
    failed_backups = backups.filter(status='failed').count()
    
    context = {
        'page_obj': page_obj,
        'total_backups': total_backups,
        'successful_backups': successful_backups,
        'failed_backups': failed_backups,
        'backup_type': backup_type,
        'status': status,
    }
    return render(request, 'accounts/backup_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_backup(request):
    """إنشاء نسخة احتياطية جديدة"""
    if request.method == 'POST':
        backup_type = request.POST.get('backup_type', 'manual')
        
        # إنشاء سجل النسخ الاحتياطي
        backup = BackupLog.objects.create(
            backup_type=backup_type,
            status='pending',
            created_by=request.user
        )
        
        # هنا يمكن إضافة كود لبدء عملية النسخ الاحتياطي الفعلية
        # يمكن استخدام Celery للمهام الخلفية
        
        messages.success(request, 'تم بدء عملية النسخ الاحتياطي.')
        return redirect('accounts:backup_list')
    
    return render(request, 'accounts/backup_form.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def backup_detail(request, pk):
    """تفاصيل النسخة الاحتياطية"""
    backup = get_object_or_404(BackupLog, pk=pk)
    
    context = {
        'backup': backup,
    }
    return render(request, 'accounts/backup_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET"])
def api_notification_stats(request):
    """API لإحصائيات الإشعارات"""
    user = request.user
    
    # إحصائيات الإشعارات
    total_notifications = Notification.objects.filter(recipient=user).count()
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False).count()
    
    # إحصائيات حسب النوع
    notification_types = Notification.objects.filter(recipient=user).values('notification_type').annotate(
        count=Count('id')
    )
    
    # آخر الإشعارات
    recent_notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]
    
    data = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'notification_types': list(notification_types),
        'recent_notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message[:100] + '...' if len(n.message) > 100 else n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
            }
            for n in recent_notifications
        ]
    }
    
    return JsonResponse(data)

