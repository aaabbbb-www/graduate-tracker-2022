from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
import json
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from graduates.models import Graduate
from surveys.models import Survey, SurveyResponse
from accounts.models import ActivityLog
from .models import Report, ScheduledReport

@login_required
def reports_home(request):
    """صفحة إدارة التقارير الرئيسية"""
    total_reports = Report.objects.count()
    scheduled_reports = ScheduledReport.objects.filter(is_active=True).count()
    # جلب قائمة التقارير الحديثة (آخر 10 تقارير)
    recent_reports = Report.objects.order_by('-created_at')[:10]
    
    # إحصائيات سريعة
    total_graduates = Graduate.objects.count()
    total_surveys = Survey.objects.count()
    total_responses = SurveyResponse.objects.count()
    
    context = {
        'total_reports': total_reports,
        'scheduled_reports': scheduled_reports,
        'recent_reports': recent_reports,
        'total_graduates': total_graduates,
        'total_surveys': total_surveys,
        'total_responses': total_responses,
    }
    return render(request, 'reports/reports_home.html', context)

@login_required
def summary_report(request):
    """التقرير الملخص العام"""
    # إحصائيات الخريجين
    graduate_stats = {
        'total': Graduate.objects.count(),
        'employed': Graduate.objects.filter(employment_status='employed').count(),
        'unemployed': Graduate.objects.filter(employment_status='unemployed').count(),
        'seeking': Graduate.objects.filter(employment_status='seeking').count(),
    }
    
    # إحصائيات حسب التخصص
    major_stats = Graduate.objects.values('major').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # إحصائيات حسب سنة التخرج
    year_stats = Graduate.objects.extra(
        select={'year': 'YEAR(graduation_date)'}
    ).values('year').annotate(
        count=Count('id')
    ).order_by('-year')[:5]
    
    # إحصائيات الاستبيانات
    survey_stats = {
        'total': Survey.objects.count(),
        'active': Survey.objects.filter(is_active=True).count(),
        'responses': SurveyResponse.objects.count(),
    }
    
    # أحدث الأنشطة
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'graduate_stats': graduate_stats,
        'major_stats': major_stats,
        'year_stats': year_stats,
        'survey_stats': survey_stats,
        'recent_activities': recent_activities,
        'employment_rate': round((graduate_stats['employed'] / graduate_stats['total'] * 100) if graduate_stats['total'] > 0 else 0, 1),
    }
    return render(request, 'reports/summary_report.html', context)

@login_required
def employment_report(request):
    """تقرير التوظيف المفصل"""
    # إحصائيات التوظيف حسب التخصص
    employment_by_major = Graduate.objects.values('major').annotate(
        total=Count('id'),
        employed=Count('id', filter=Q(employment_status='employed')),
        unemployed=Count('id', filter=Q(employment_status='unemployed')),
        seeking=Count('id', filter=Q(employment_status='seeking'))
    ).order_by('-total')
    
    # إحصائيات التوظيف حسب سنة التخرج
    employment_by_year = Graduate.objects.extra(
        select={'year': 'YEAR(graduation_date)'}
    ).values('year').annotate(
        total=Count('id'),
        employed=Count('id', filter=Q(employment_status='employed'))
    ).order_by('-year')
    
    # إحصائيات التوظيف حسب المدينة
    employment_by_city = Graduate.objects.values('city').annotate(
        total=Count('id'),
        employed=Count('id', filter=Q(employment_status='employed'))
    ).order_by('-total')[:10]
    
    context = {
        'employment_by_major': employment_by_major,
        'employment_by_year': employment_by_year,
        'employment_by_city': employment_by_city,
    }
    return render(request, 'reports/employment_report.html', context)

@login_required
def survey_report(request):
    """تقرير الاستبيانات"""
    surveys = Survey.objects.annotate(
        response_count=Count('responses')
    ).order_by('-created_at')
    
    # إحصائيات الاستبيانات
    survey_stats = {
        'total': surveys.count(),
        'active': surveys.filter(status='active').count(),
        'total_responses': SurveyResponse.objects.count(),
        'avg_responses': round(SurveyResponse.objects.count() / surveys.count() if surveys.count() > 0 else 0, 1),
    }
    
    # أكثر الاستبيانات استجابة
    top_surveys = surveys.order_by('-response_count')[:5]
    
    # إحصائيات شهرية للاستجابات
    monthly_responses = SurveyResponse.objects.extra(
        select={'month': 'MONTH(submitted_at)', 'year': 'YEAR(submitted_at)'}
    ).values('month', 'year').annotate(
        count=Count('id')
    ).order_by('-year', '-month')[:12]
    
    context = {
        'surveys': surveys,
        'survey_stats': survey_stats,
        'top_surveys': top_surveys,
        'monthly_responses': monthly_responses,
    }
    return render(request, 'reports/survey_report.html', context)

@login_required
def custom_report(request):
    """إنشاء تقرير مخصص"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        filters = request.POST.getlist('filters')
        
        # إنشاء التقرير المخصص
        report_data = generate_custom_report(report_type, date_from, date_to, filters)
        
        # حفظ التقرير
        report = Report.objects.create(
            title=f'تقرير مخصص - {report_type}',
            description=f'تقرير من {date_from} إلى {date_to}',
            report_type=report_type,
            data=json.dumps(report_data),
            created_by=request.user
        )
        
        messages.success(request, 'تم إنشاء التقرير المخصص بنجاح!')
        return redirect('reports:view_report', pk=report.pk)
    
    context = {
        'majors': Graduate.objects.values_list('major', flat=True).distinct(),
        'cities': Graduate.objects.values_list('city', flat=True).distinct(),
        'surveys': Survey.objects.all(),
    }
    return render(request, 'reports/custom_report.html', context)

@login_required
def scheduled_reports(request):
    """التقارير المجدولة"""
    reports = ScheduledReport.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        # إنشاء تقرير مجدول جديد
        title = request.POST.get('title')
        report_type = request.POST.get('report_type')
        schedule_type = request.POST.get('schedule_type')
        recipients = request.POST.get('recipients')
        
        ScheduledReport.objects.create(
            title=title,
            report_type=report_type,
            schedule_type=schedule_type,
            recipients=recipients,
            created_by=request.user
        )
        
        messages.success(request, 'تم إنشاء التقرير المجدول بنجاح!')
        return redirect('reports:scheduled')
    
    context = {'reports': reports}
    return render(request, 'reports/scheduled_reports.html', context)

@login_required
def analytics_dashboard(request):
    """لوحة التحليلات المتقدمة"""
    # بيانات للرسوم البيانية
    employment_data = {
        'employed': Graduate.objects.filter(employment_status='employed').count(),
        'unemployed': Graduate.objects.filter(employment_status='unemployed').count(),
        'seeking': Graduate.objects.filter(employment_status='seeking').count(),
    }
    
    # بيانات التخصصات
    major_data = list(Graduate.objects.values('major').annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    # بيانات الاستجابات الشهرية
    monthly_data = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        count = SurveyResponse.objects.filter(
            submitted_at__year=date.year,
            submitted_at__month=date.month
        ).count()
        monthly_data.append({
            'month': date.strftime('%Y-%m'),
            'count': count
        })
    
    context = {
        'employment_data': json.dumps(employment_data),
        'major_data': json.dumps(major_data),
        'monthly_data': json.dumps(list(reversed(monthly_data))),
    }
    return render(request, 'reports/analytics_dashboard.html', context)

@login_required
def export_reports(request):
    """تصدير التقارير"""
    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        report_format = request.POST.get('format')
        
        if export_type == 'graduates':
            return export_graduates_report(report_format)
        elif export_type == 'surveys':
            return export_surveys_report(report_format)
        elif export_type == 'employment':
            return export_employment_report(report_format)
    
    return render(request, 'reports/export_reports.html')

@login_required
def view_report(request, pk):
    """عرض تقرير محفوظ"""
    report = get_object_or_404(Report, pk=pk)
    data = json.loads(report.data) if report.data else {}
    
    context = {
        'report': report,
        'data': data,
    }
    return render(request, 'reports/view_report.html', context)

@login_required
def export_options(request):
    """صفحة خيارات التصدير (تحت التطوير)"""
    return render(request, 'reports/export_options.html')

@login_required
def bulk_export(request):
    """صفحة تصدير جماعي (تحت التطوير)"""
    return render(request, 'reports/bulk_export.html')

@login_required
def quick_summary(request):
    """عرض ملخص سريع للتقارير والإحصائيات الرئيسية"""
    return render(request, 'reports/quick_summary.html')

@login_required
def data_export(request):
    """صفحة تصدير البيانات"""
    return render(request, 'reports/data_export.html')

@login_required
def report_templates(request):
    """صفحة قوالب التقارير"""
    return render(request, 'reports/report_templates.html')

@login_required
def report_settings(request):
    """صفحة إعدادات التقارير"""
    return render(request, 'reports/report_settings.html')

def generate_custom_report(report_type, date_from, date_to, filters):
    """إنشاء تقرير مخصص"""
    data = {}
    
    if report_type == 'graduates':
        queryset = Graduate.objects.all()
        if date_from:
            queryset = queryset.filter(graduation_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(graduation_date__lte=date_to)
        
        data = {
            'total': queryset.count(),
            'by_major': list(queryset.values('major').annotate(count=Count('id'))),
            'by_employment': list(queryset.values('employment_status').annotate(count=Count('id'))),
        }
    
    elif report_type == 'surveys':
        queryset = Survey.objects.all()
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        data = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'responses': SurveyResponse.objects.filter(survey__in=queryset).count(),
        }
    
    return data

def export_graduates_report(format_type):
    """تصدير تقرير الخريجين"""
    graduates = Graduate.objects.all()
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="graduates_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['الاسم الأول', 'الاسم الأخير', 'البريد الإلكتروني', 'التخصص', 'تاريخ التخرج', 'حالة التوظيف'])
        
        for graduate in graduates:
            writer.writerow([
                graduate.first_name,
                graduate.last_name,
                graduate.email,
                graduate.major,
                graduate.graduation_date,
                graduate.get_employment_status_display()
            ])
        
        return response
    
    elif format_type == 'pdf':
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # إضافة العنوان
        styles = getSampleStyleSheet()
        title = Paragraph("تقرير الخريجين", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # إضافة الجدول
        data = [['الاسم', 'البريد الإلكتروني', 'التخصص', 'حالة التوظيف']]
        for graduate in graduates[:50]:  # أول 50 خريج
            data.append([
                f"{graduate.first_name} {graduate.last_name}",
                graduate.email,
                graduate.major,
                graduate.get_employment_status_display()
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="graduates_report.pdf"'
        return response

def export_surveys_report(format_type):
    """تصدير تقرير الاستبيانات"""
    #مشابه لتصدير تقرير الخريجين
    pass

def export_employment_report(format_type):
    """تصدير تقرير التوظيف"""
    #مشابه لتصدير تقرير الخريجين
    pass

@login_required
@require_http_methods(["GET"])
def api_employment_trends(request):
    """API لبيانات اتجاهات التوظيف"""
    # بيانات آخر 12 شهر
    months_data = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        employed = Graduate.objects.filter(
            employment_status='employed',
            graduation_date__year=date.year,
            graduation_date__month=date.month
        ).count()
        months_data.append({
            'month': date.strftime('%Y-%m'),
            'employed': employed
        })
    
    data = {
        'labels': [item['month'] for item in reversed(months_data)],
        'data': [item['employed'] for item in reversed(months_data)]
    }
    return JsonResponse(data)

@login_required
@require_http_methods(["GET"])
def api_survey_responses_chart(request):
    """API لبيانات الرسم البياني لاستجابات الاستبيانات"""
    # بيانات آخر 6 أشهر
    months_data = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        count = SurveyResponse.objects.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        months_data.append({
            'month': date.strftime('%Y-%m'),
            'count': count
        })
    
    data = {
        'labels': [item['month'] for item in reversed(months_data)],
        'data': [item['count'] for item in reversed(months_data)]
    }
    return JsonResponse(data)

@login_required
def graduates_summary(request):
    """
    تقرير شامل للخريجين مع إمكانية التصفية حسب الكلية أو القسم أو سنة التخرج
    """
    graduates = Graduate.objects.all()
    college = request.GET.get('college')
    major = request.GET.get('major')
    graduation_year = request.GET.get('graduation_year')
    if college:
        graduates = graduates.filter(college__icontains=college)
    if major:
        graduates = graduates.filter(major__icontains=major)
    if graduation_year:
        graduates = graduates.filter(graduation_year=graduation_year)

    total = graduates.count()
    by_gender = graduates.values('gender').annotate(count=Count('id'))
    by_year = graduates.values('graduation_year').annotate(count=Count('id')).order_by('graduation_year')
    by_major = graduates.values('major').annotate(count=Count('id')).order_by('-count')[:10]

    # إحصائيات الاستبيانات
    survey_sent = SurveyResponse.objects.filter(graduate__in=graduates).count()
    survey_answered = SurveyResponse.objects.filter(graduate__in=graduates, is_complete=True).count()
    survey_not_sent = total - survey_sent

    # معدل التوظيف
    employed_count = graduates.filter(employment_status='employed').count()
    employment_rate = round((employed_count / total) * 100, 1) if total else 0

    # الرضا عن جودة التعليم (مثال: سؤال نصي أو اختياري في الاستبيان)
    satisfied_education = SurveyResponse.objects.filter(graduate__in=graduates, answers__answer_text__icontains='راض', answers__question__question_text__icontains='جودة التعليم').count()
    unsatisfied_programs = SurveyResponse.objects.filter(graduate__in=graduates, answers__answer_text__icontains='غير راض', answers__question__question_text__icontains='البرامج').count()

    # أهم 3 اقتراحات (مثال: سؤال نصي في الاستبيان)
    from django.db.models import Count as DCount
    suggestions = SurveyResponse.objects.filter(graduate__in=graduates, answers__question__question_text__icontains='اقتراح').values('answers__answer_text').annotate(count=DCount('answers__answer_text')).order_by('-count')[:3]
    top_suggestions = [{'suggestion': s['answers__answer_text'], 'count': s['count']} for s in suggestions if s['answers__answer_text']]

    context = {
        'graduates': graduates,
        'total': total,
        'by_gender': by_gender,
        'by_year': by_year,
        'by_major': by_major,
        'survey_sent': survey_sent,
        'survey_not_sent': survey_not_sent,
        'survey_answered': survey_answered,
        'satisfied_education': satisfied_education,
        'unsatisfied_programs': unsatisfied_programs,
        'employment_rate': employment_rate,
        'top_suggestions': top_suggestions,
        'request': request,
    }
    return render(request, 'reports/graduates_summary.html', context)

@login_required
def graduates_analytics(request):
    """
    صفحة التحليلات المتقدمة للخريجين: رسوم بيانية وتحليلات ديموغرافية وتوزيعات
    """
    from graduates.models import Graduate
    by_year = Graduate.objects.values('graduation_year').annotate(count=Count('id')).order_by('graduation_year')
    by_major = Graduate.objects.values('major').annotate(count=Count('id')).order_by('-count')[:10]
    avg_gpa = Graduate.objects.aggregate(avg_gpa=Avg('gpa'))['avg_gpa']
    context = {
        'by_year': by_year,
        'by_major': by_major,
        'avg_gpa': avg_gpa,
    }
    return render(request, 'reports/graduates_analytics.html', context)

@login_required
def salary_analysis(request):
    """
    تحليل الرواتب للخريجين: إحصائيات ورسوم بيانية حول الرواتب
    """
    # هنا يمكن ربط البيانات الحقيقية لاحقاً
    return render(request, 'reports/salary_analysis.html')

@login_required
def response_analysis(request):
    """
    تحليل الاستجابات للاستبيانات: إحصائيات ورسوم بيانية
    """
    return render(request, 'reports/response_analysis.html')

@login_required
def interactive_dashboard(request):
    """
    لوحة تحكم تفاعلية: رسوم بيانية ديناميكية وفلاتر
    """
    return render(request, 'reports/interactive_dashboard.html')

@login_required
def custom_charts(request):
    """
    رسوم بيانية مخصصة: أدوات رسم وتحليل مخصصة
    """
    return render(request, 'reports/custom_charts.html')

@login_required
def schedule_report(request):
    """
    جدولة تقرير جديد: نموذج جدولة وإدارة التقارير الدورية
    """
    return render(request, 'reports/schedule_report.html')

@login_required
def education_quality_analysis(request):
    """
    تحليل جودة التعليم والبرامج الدراسية: إحصائيات حول رضا الخريجين، تقييم البرامج، ونسب التوظيف حسب البرنامج
    مع دعم التصفية حسب الكلية/القسم/سنة التخرج
    """
    from graduates.models import Graduate
    from surveys.models import SurveyResponse, Answer, Question
    
    # --- فلاتر ---
    college = request.GET.get('college')
    major = request.GET.get('major')
    year = request.GET.get('year')
    
    graduates_qs = Graduate.objects.all()
    if college:
        graduates_qs = graduates_qs.filter(college=college)
    if major:
        graduates_qs = graduates_qs.filter(major=major)
    if year:
        graduates_qs = graduates_qs.filter(graduation_year=year)

    # حساب نسبة التوظيف حسب البرنامج
    by_program = graduates_qs.values('major').annotate(
        total=Count('id'),
        employed=Count('id', filter=Q(employment_status='employed'))
    ).order_by('-total')

    # استخراج متوسط تقييم جودة التعليم من إجابات الأسئلة ذات العلاقة
    quality_questions = Question.objects.filter(
        question_type='rating',
        question_text__icontains='جودة التعليم'
    )
    answers = Answer.objects.filter(question__in=quality_questions)
    if college or major or year:
        # تصفية الإجابات حسب الخريجين في النطاق
        answers = answers.filter(response__graduate__in=graduates_qs)
    avg_quality = answers.aggregate(avg=Avg('answer_number'))['avg']

    # إحصائيات المشاركة
    graduates_count = graduates_qs.count()
    responses_count = SurveyResponse.objects.filter(graduate__in=graduates_qs).count()

    # خيارات الفلاتر
    colleges = Graduate.objects.values_list('college', flat=True).distinct()
    majors = Graduate.objects.values_list('major', flat=True).distinct()
    years = Graduate.objects.values_list('graduation_year', flat=True).distinct().order_by('-graduation_year')

    context = {
        'by_program': by_program,
        'avg_quality': avg_quality,
        'colleges': colleges,
        'majors': majors,
        'years': years,
        'selected_college': college,
        'selected_major': major,
        'selected_year': year,
        'graduates_count': graduates_count,
        'responses_count': responses_count,
    }
    return render(request, 'reports/education_quality_analysis.html', context)

