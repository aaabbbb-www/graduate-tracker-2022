from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import json
import csv
from .models import Graduate
from .forms import GraduateForm

@login_required
def graduates_home(request):
    """صفحة إدارة الخريجين الرئيسية"""
    total_graduates = Graduate.objects.count()
    employed_graduates = Graduate.objects.filter(employment_status='employed').count()
    unemployed_graduates = Graduate.objects.filter(employment_status='unemployed').count()
    seeking_graduates = Graduate.objects.filter(employment_status='seeking').count()
    
    # إحصائيات إضافية
    recent_graduates = Graduate.objects.filter(graduation_year=2024).count()
    
    context = {
        'total_graduates': total_graduates,
        'employed_graduates': employed_graduates,
        'unemployed_graduates': unemployed_graduates,
        'seeking_graduates': seeking_graduates,
        'recent_graduates': recent_graduates,
        'employment_rate': round((employed_graduates / total_graduates * 100) if total_graduates > 0 else 0, 1),
    }
    return render(request, 'graduates/graduates_home.html', context)

@login_required
def graduate_list(request):
    """قائمة الخريجين مع البحث والفلترة"""
    graduates = Graduate.objects.all().order_by('-graduation_year')
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        graduates = graduates.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # الفلترة حسب التخصص
    major_filter = request.GET.get('major')
    if major_filter:
        graduates = graduates.filter(major__icontains=major_filter)
    
    # الفلترة حسب حالة التوظيف
    employment_filter = request.GET.get('employment_status')
    if employment_filter:
        graduates = graduates.filter(employment_status=employment_filter)
    
    # التقسيم إلى صفحات
    paginator = Paginator(graduates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'major_filter': major_filter,
        'employment_filter': employment_filter,
    }
    return render(request, 'graduates/graduate_list.html', context)

@login_required
def graduate_create(request):
    """إضافة خريج جديد"""
    if request.method == 'POST':
        form = GraduateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الخريج بنجاح!')
            return redirect('graduates:list')
        else:
            messages.error(request, 'فشل في إضافة الخريج. يرجى تصحيح الأخطاء أدناه.')
    else:
        form = GraduateForm()
    return render(request, 'graduates/graduate_form.html', {'form': form, 'title': 'إضافة خريج جديد'})

@login_required
def graduate_update(request, pk):
    """تعديل بيانات خريج"""
    graduate = get_object_or_404(Graduate, pk=pk)
    
    if request.method == 'POST':
        form = GraduateForm(request.POST, instance=graduate)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات الخريج بنجاح!')
            return redirect('graduates:list')
    else:
        form = GraduateForm(instance=graduate)
    
    return render(request, 'graduates/graduate_form.html', {'form': form, 'title': 'تعديل بيانات الخريج'})

@login_required
def graduate_delete(request, pk):
    """حذف خريج"""
    graduate = get_object_or_404(Graduate, pk=pk)
    
    if request.method == 'POST':
        graduate.delete()
        messages.success(request, 'تم حذف الخريج بنجاح!')
        return redirect('graduates:list')
    
    return render(request, 'graduates/graduate_confirm_delete.html', {'graduate': graduate})

@login_required
def graduate_detail(request, pk):
    """تفاصيل خريج"""
    graduate = get_object_or_404(Graduate, pk=pk)
    return render(request, 'graduates/graduate_detail.html', {'graduate': graduate})

@login_required
def graduate_search(request):
    """البحث المتقدم في الخريجين"""
    context = {
        'majors': Graduate.objects.values_list('major', flat=True).distinct(),
        'cities': Graduate.objects.values_list('city', flat=True).distinct(),
    }
    return render(request, 'graduates/graduate_search.html', context)

@login_required
def employment_statistics(request):
    """إحصائيات التوظيف"""
    # إحصائيات حسب التخصص
    major_stats = Graduate.objects.values('major').annotate(
        total=Count('id'),
        employed=Count('id', filter=Q(employment_status='employed')),
        unemployed=Count('id', filter=Q(employment_status='unemployed')),
        seeking=Count('id', filter=Q(employment_status='seeking'))
    ).order_by('-total')
    
    # إحصائيات حسب سنة التخرج
    year_stats = Graduate.objects.values('graduation_year').annotate(
        total=Count('id'),
        employed=Count('id', filter=Q(employment_status='employed'))
    ).order_by('-graduation_year')
    
    context = {
        'major_stats': major_stats,
        'year_stats': year_stats,
    }
    return render(request, 'graduates/employment_statistics.html', context)

@login_required
def analytics_dashboard(request):
    """لوحة التحليلات والرسوم البيانية"""
    # بيانات للرسوم البيانية
    employment_data = {
        'employed': Graduate.objects.filter(employment_status='employed').count(),
        'unemployed': Graduate.objects.filter(employment_status='unemployed').count(),
        'seeking': Graduate.objects.filter(employment_status='seeking').count(),
    }
    
    # بيانات التخصصات
    major_data = list(Graduate.objects.values('major').annotate(count=Count('id')).order_by('-count')[:10])
    
    context = {
        'employment_data': json.dumps(employment_data),
        'major_data': json.dumps(major_data),
    }
    return render(request, 'graduates/analytics_dashboard.html', context)

@login_required
def import_export(request):
    """صفحة استيراد وتصدير البيانات"""
    if request.method == 'POST':
        if 'export' in request.POST:
            # تصدير البيانات إلى CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="graduates.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['الاسم الأول', 'الاسم الأخير', 'البريد الإلكتروني', 'الهاتف', 'التخصص', 'تاريخ التخرج', 'حالة التوظيف'])
            
            for graduate in Graduate.objects.all():
                writer.writerow([
                    graduate.first_name,
                    graduate.last_name,
                    graduate.email,
                    graduate.phone,
                    graduate.major,
                    graduate.graduation_year,
                    graduate.get_employment_status_display()
                ])
            
            return response
    
    return render(request, 'graduates/import_export.html')

@login_required
@require_http_methods(["GET"])
def api_employment_chart_data(request):
    """API لبيانات الرسم البياني للتوظيف"""
    data = {
        'labels': ['موظف', 'عاطل', 'يبحث عن عمل'],
        'data': [
            Graduate.objects.filter(employment_status='employed').count(),
            Graduate.objects.filter(employment_status='unemployed').count(),
            Graduate.objects.filter(employment_status='seeking').count(),
        ]
    }
    return JsonResponse(data)

