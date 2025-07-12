from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Max
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import json
import secrets
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from .models import Survey, Question, SurveyResponse, Answer, QuestionChoice, SurveyTemplate, SurveyInvitation, SurveySendLog
from .forms import SurveyForm, QuestionForm, ChoiceForm, SurveyTemplateForm, FlexibleSurveyForm, FlexibleQuestionForm, NewSurveyForm, NewQuestionForm
from graduates.models import Graduate
from django.template.loader import render_to_string
from .utils import SurveySender
from django.utils.html import strip_tags
import secrets

@login_required
def surveys_home(request):
    """صفحة إدارة الاستبيانات الرئيسية"""
    total_surveys = Survey.objects.count()
    active_surveys = Survey.objects.filter(status='active').count()
    total_responses = SurveyResponse.objects.count()
    sent_surveys = Survey.objects.filter(responses__isnull=False).distinct().count()
    pending_surveys = Survey.objects.filter(status='active', responses__isnull=True).distinct().count()
    
    # حساب معدل الاستجابة
    total_sent = SurveyInvitation.objects.filter(status='sent').count()
    response_rate = round((total_responses / total_sent * 100) if total_sent > 0 else 0, 1)
    
    context = {
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'total_responses': total_responses,
        'sent_surveys': sent_surveys,
        'pending_surveys': pending_surveys,
        'response_rate': response_rate,
    }
    return render(request, 'surveys/surveys_home.html', context)

@login_required
def survey_list(request):
    """قائمة الاستبيانات"""
    surveys = Survey.objects.all().order_by('-created_at')
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        surveys = surveys.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # الفلترة حسب الحالة
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        surveys = surveys.filter(status='active')
    elif status_filter == 'inactive':
        surveys = surveys.filter(status='closed')
    
    # التقسيم إلى صفحات
    paginator = Paginator(surveys, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'surveys/survey_list.html', context)

@login_required
def flexible_survey_create(request):
    """إنشاء استبيان مرن ومحسن"""
    if request.method == 'POST':
        form = FlexibleSurveyForm(request.POST, request.FILES)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            
            # حفظ الخريجين المختارين
            selected_graduates = form.cleaned_data.get('selected_graduates', [])
            
            # إرسال تلقائي إذا كان مفعلاً
            if form.cleaned_data.get('auto_send') and selected_graduates:
                sender = SurveySender()
                results = sender.send_survey(survey, selected_graduates, request)
                
                # إظهار رسائل النجاح والفشل
                success_count = results['total_sent']
                failed_count = results['total_failed']
                
                if success_count > 0:
                    messages.success(request, f'تم إنشاء الاستبيان وإرساله إلى {success_count} خريج بنجاح!')
                
                if failed_count > 0:
                    messages.warning(request, f'فشل في إرسال الاستبيان إلى {failed_count} خريج.')
                
                # إظهار تفاصيل الإرسال
                if results['email']:
                    email_success = sum(1 for r in results['email'] if r['success'])
                    email_failed = len(results['email']) - email_success
                    if email_success > 0:
                        messages.info(request, f'تم إرسال {email_success} بريد إلكتروني بنجاح.')
                    if email_failed > 0:
                        messages.warning(request, f'فشل في إرسال {email_failed} بريد إلكتروني.')
                
                if results['whatsapp']:
                    whatsapp_success = sum(1 for r in results['whatsapp'] if r['success'])
                    whatsapp_failed = len(results['whatsapp']) - whatsapp_success
                    if whatsapp_success > 0:
                        messages.info(request, f'تم إنشاء {whatsapp_success} رابط واتساب.')
                    if whatsapp_failed > 0:
                        messages.warning(request, f'فشل في إنشاء {whatsapp_failed} رابط واتساب.')
            else:
                messages.success(request, 'تم إنشاء الاستبيان بنجاح! يمكنك الآن إضافة الأسئلة.')
            
            return redirect('surveys:flexible_detail', pk=survey.pk)
    else:
        form = FlexibleSurveyForm()
    
    return render(request, 'surveys/flexible_survey_form.html', {
        'form': form, 
        'title': 'إنشاء استبيان جديد'
    })

@login_required
def flexible_survey_detail(request, pk):
    """تفاصيل الاستبيان المرن"""
    survey = get_object_or_404(Survey, pk=pk)
    questions = survey.questions.all().order_by('order')
    responses_count = survey.responses.count()
    
    context = {
        'survey': survey,
        'questions': questions,
        'responses_count': responses_count,
    }
    return render(request, 'surveys/flexible_survey_detail.html', context)

@login_required
def flexible_question_create(request, survey_pk):
    """إضافة سؤال مرن إلى الاستبيان"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    
    if request.method == 'POST':
        form = FlexibleQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.order = survey.questions.count() + 1
            question.save()
            
            # إضافة الخيارات إذا كانت موجودة
            choices_text = form.cleaned_data.get('choices_text', '')
            if choices_text and question.question_type in ['radio', 'checkbox', 'select']:
                choices = [choice.strip() for choice in choices_text.split('\n') if choice.strip()]
                for i, choice_text in enumerate(choices):
                    QuestionChoice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        order=i + 1
                    )
            
            messages.success(request, 'تم إضافة السؤال بنجاح!')
            return redirect('surveys:flexible_detail', pk=survey.pk)
    else:
        form = FlexibleQuestionForm()
    
    return render(request, 'surveys/flexible_question_form.html', {
        'form': form, 
        'survey': survey, 
        'title': 'إضافة سؤال جديد'
    })

@login_required
def survey_create(request):
    """إنشاء استبيان جديد"""
    if request.method == 'POST':
        form = SurveyForm(request.POST, request.FILES)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            
            # حفظ الخريجين المختارين
            selected_graduates = form.cleaned_data.get('selected_graduates', [])
            
            # إرسال تلقائي إذا كان مفعلاً
            if form.cleaned_data.get('auto_send') and selected_graduates:
                sender = SurveySender()
                results = sender.send_survey(survey, selected_graduates, request)
                
                # إظهار رسائل النجاح والفشل
                success_count = results['total_sent']
                failed_count = results['total_failed']
                
                if success_count > 0:
                    messages.success(request, f'تم إنشاء الاستبيان وإرساله إلى {success_count} خريج بنجاح!')
                
                if failed_count > 0:
                    messages.warning(request, f'فشل في إرسال الاستبيان إلى {failed_count} خريج.')
                
                # إظهار تفاصيل الإرسال
                if results['email']:
                    email_success = sum(1 for r in results['email'] if r['success'])
                    email_failed = len(results['email']) - email_success
                    if email_success > 0:
                        messages.info(request, f'تم إرسال {email_success} بريد إلكتروني بنجاح.')
                    if email_failed > 0:
                        messages.warning(request, f'فشل في إرسال {email_failed} بريد إلكتروني.')
                
                if results['whatsapp']:
                    whatsapp_success = sum(1 for r in results['whatsapp'] if r['success'])
                    whatsapp_failed = len(results['whatsapp']) - whatsapp_success
                    if whatsapp_success > 0:
                        messages.info(request, f'تم إنشاء {whatsapp_success} رابط واتساب.')
                    if whatsapp_failed > 0:
                        messages.warning(request, f'فشل في إنشاء {whatsapp_failed} رابط واتساب.')
            else:
                messages.success(request, 'تم إنشاء الاستبيان بنجاح!')
            
            return redirect('surveys:detail', pk=survey.pk)
    else:
        form = SurveyForm()
    
    return render(request, 'surveys/survey_form.html', {'form': form, 'title': 'إنشاء استبيان جديد'})

@login_required
def survey_detail(request, pk):
    """تفاصيل الاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    questions = survey.questions.all().order_by('order')
    responses_count = survey.responses.count()
    
    context = {
        'survey': survey,
        'questions': questions,
        'responses_count': responses_count,
    }
    return render(request, 'surveys/survey_detail.html', context)

@login_required
def survey_update(request, pk):
    """تعديل استبيان مع دعم تعديل/حذف/إضافة الأسئلة"""
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        form = NewSurveyForm(request.POST, request.FILES, instance=survey)
        if form.is_valid():
            form.save()
            # حذف جميع الأسئلة القديمة (سيتم إعادة إضافتها)
            survey.questions.all().delete()
            # إضافة الأسئلة الجديدة
            questions_data = request.POST.getlist('questions[]')
            for qdata in questions_data:
                import json
                qobj = json.loads(qdata)
                question = Question.objects.create(
                    survey=survey,
                    question_text=qobj['text'],
                    question_type=qobj['type'],
                    order=int(qobj['order']) if qobj.get('order') else 0,
                    is_required=True
                )
                # إذا كان هناك خيارات
                if qobj['type'] in ['radio', 'checkbox', 'select'] and qobj.get('choices'):
                    choices = [c.strip() for c in qobj['choices'].split('\n') if c.strip()]
                    for i, choice_text in enumerate(choices):
                        QuestionChoice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            order=i+1
                        )
            messages.success(request, 'تم تحديث الاستبيان بنجاح!')
            return redirect('surveys:detail', pk=survey.pk)
    else:
        form = NewSurveyForm(instance=survey)
    questions = survey.questions.all().order_by('order')
    return render(request, 'surveys/edit_survey.html', {'form': form, 'survey': survey, 'questions': questions, 'title': 'تعديل الاستبيان'})

@login_required
def survey_delete(request, pk):
    """حذف استبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'تم حذف الاستبيان بنجاح.')
        return redirect('surveys:list')
    return render(request, 'surveys/survey_confirm_delete.html', {'survey': survey})

@login_required
def send_survey_select(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    graduates = Graduate.objects.filter(is_active=True).order_by('first_name')

    if request.method == 'POST':
        graduate_ids = request.POST.getlist('graduates')
        if not graduate_ids:
            messages.error(request, 'يرجى تحديد خريج واحد على الأقل.')
            return redirect('surveys:send_survey_select', pk=pk)

        selected_graduates = Graduate.objects.filter(id__in=graduate_ids)
        success_count = 0
        fail_count = 0

        for graduate in selected_graduates:
            if graduate.email:
                try:
                    # Create a unique invitation token
                    invitation, created = SurveyInvitation.objects.get_or_create(
                        survey=survey,
                        graduate=graduate,
                        defaults={'token': secrets.token_urlsafe(20)}
                    )

                    # Generate the survey link
                    survey_link = request.build_absolute_uri(
                        reverse('surveys:take_survey_by_token', kwargs={'token': invitation.token})
                    )

                    # Email subject and content
                    subject = f'دعوة للمشاركة في استبيان: {survey.title}'
                    html_message = render_to_string('surveys/survey_email_template.html', {
                        'survey_title': survey.title,
                        'graduate_name': graduate.full_name,
                        'survey_link': survey_link,
                        'survey_description': survey.description
                    })
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [graduate.email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    invitation.status = 'sent'
                    invitation.sent_at = timezone.now()
                    invitation.save()
                    success_count += 1
                    SurveySendLog.objects.create(survey=survey, graduate=graduate, status='success', channel='email')
                except Exception as e:
                    fail_count += 1
                    SurveySendLog.objects.create(survey=survey, graduate=graduate, status='failed', channel='email', details=str(e))
            else:
                fail_count += 1
                SurveySendLog.objects.create(survey=survey, graduate=graduate, status='failed', channel='email', details='No email address')

        if success_count > 0:
            messages.success(request, f'تم إرسال الاستبيان بنجاح إلى {success_count} خريج عبر البريد الإلكتروني.')
        if fail_count > 0:
            messages.warning(request, f'فشل إرسال الاستبيان إلى {fail_count} خريج لعدم وجود بريد إلكتروني أو خطأ في الإرسال.')

        return redirect('surveys:detail', pk=survey.pk)

    return render(request, 'surveys/send_survey_select.html', {
        'survey': survey,
        'graduates': graduates
    })

def take_survey_by_token(request, invitation_token):
    invitation = get_object_or_404(SurveyInvitation, invitation_token=invitation_token)
    survey = invitation.survey

    # التحقق من صلاحية الاستبيان والدعوة
    if survey.status != 'active' or (survey.end_date and survey.end_date < timezone.now()):
        messages.error(request, 'هذا الاستبيان غير متاح حالياً.')
        return render(request, 'surveys/survey_unavailable.html', {'survey': survey})

    if invitation.status == 'completed':
        messages.info(request, 'لقد قمت بإكمال هذا الاستبيان مسبقاً. شكراً لمشاركتك.')
        return render(request, 'surveys/survey_unavailable.html', {'survey': survey})

    # تحديث حالة الدعوة إلى 'تم الفتح'
    if invitation.status == 'sent':
        invitation.status = 'opened'
        invitation.opened_at = timezone.now()
        invitation.save()

    if request.method == 'POST':
        response, created = SurveyResponse.objects.get_or_create(
            survey=survey,
            graduate=invitation.graduate
        )

        for question in survey.questions.all():
            answer_value = request.POST.get(f'question_{question.pk}')
            if answer_value:
                Answer.objects.update_or_create(
                    response=response,
                    question=question,
                    defaults={'text_answer': answer_value}
                )

        response.is_complete = True
        response.save()

        invitation.status = 'completed'
        invitation.completed_at = timezone.now()
        invitation.save()

        messages.success(request, 'شكراً لك! تم إرسال إجاباتك بنجاح.')
        return redirect('surveys:thank_you', pk=survey.pk)

    return render(request, 'surveys/take_survey.html', {'survey': survey, 'questions': survey.questions.all().order_by('order')})


@login_required
def question_create(request, survey_pk):
    """إضافة سؤال إلى الاستبيان"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.order = survey.questions.count() + 1
            question.save()
            messages.success(request, 'تم إضافة السؤال بنجاح!')
            return redirect('surveys:detail', pk=survey.pk)
    else:
        form = QuestionForm()
    
    return render(request, 'surveys/question_form.html', {
        'form': form, 
        'survey': survey, 
        'title': 'إضافة سؤال جديد'
    })

@login_required
def send_survey_select(request):
    """صفحة اختيار الاستبيان للإرسال"""
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'surveys/send_survey_select.html', {
        'surveys': surveys
    })

@login_required
def send_survey(request, pk=None):
    """إرسال الاستبيان"""
    if pk is None:
        # إذا لم يتم تحديد استبيان، اعرض صفحة اختيار الاستبيان
        return send_survey_select(request)
    
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        selected_graduates = request.POST.getlist('graduates')
        if selected_graduates:
            graduates = Graduate.objects.filter(id__in=selected_graduates)
            sender = SurveySender()
            successful_sends, failed_sends = sender.send_invitations(survey, selected_graduates, request)

            success_count = len(successful_sends)
            failed_count = len(failed_sends)

            if success_count > 0:
                messages.success(request, f'تم إرسال الاستبيان إلى {success_count} خريج بنجاح!')

            if failed_count > 0:
                failed_names = ', '.join([g.full_name for g, e in failed_sends])
                messages.warning(request, f'فشل إرسال الاستبيان إلى {failed_count} خريج: {failed_names}. يرجى مراجعة سجلات الإرسال لمزيد من التفاصيل.')
            
            return redirect('surveys:detail', pk=survey.pk)
    
    graduates = Graduate.objects.all()
    return render(request, 'surveys/send_survey.html', {
        'survey': survey,
        'graduates': graduates
    })

@login_required
def take_survey(request, pk):
    """ملء الاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        # حفظ الاستجابة
        response = SurveyResponse.objects.create(
            survey=survey,
            respondent_name=request.POST.get('respondent_name', ''),
            respondent_email=request.POST.get('respondent_email', ''),
            submitted_at=timezone.now()
        )
        
        # حفظ الإجابات
        for question in survey.questions.all():
            answer_text = request.POST.get(f'question_{question.id}')
            if answer_text:
                Answer.objects.create(
                    response=response,
                    question=question,
                    text_answer=answer_text
                )
        
        messages.success(request, 'تم إرسال الاستبيان بنجاح!')
        return redirect('surveys:thank_you', pk=survey.pk)
    
    return render(request, 'surveys/take_survey.html', {'survey': survey})

@login_required
def survey_thank_you(request, pk):
    """صفحة شكر بعد ملء الاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    return render(request, 'surveys/survey_thank_you.html', {'survey': survey})

@login_required
def survey_results(request, pk):
    """نتائج الاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    responses = survey.responses.all().order_by('-submitted_at')
    
    # إحصائيات عامة
    total_responses = responses.count()
    questions = survey.questions.all()
    
    # تحليل الإجابات لكل سؤال
    question_analysis = []
    for question in questions:
        answers = Answer.objects.filter(question=question)
        if question.question_type == 'multiple_choice':
            choice_counts = {}
            for choice in question.choices.all():
                count = answers.filter(text_answer=choice.text).count()
                choice_counts[choice.text] = count
            question_analysis.append({
                'question': question,
                'type': 'multiple_choice',
                'choice_counts': choice_counts,
                'total_answers': answers.count()
            })
        else:
            question_analysis.append({
                'question': question,
                'type': 'text',
                'answers': answers[:10],  # أول 10 إجابات فقط
                'total_answers': answers.count()
            })
    
    context = {
        'survey': survey,
        'responses': responses,
        'total_responses': total_responses,
        'question_analysis': question_analysis,
    }
    return render(request, 'surveys/survey_results.html', context)

@login_required
def survey_analytics(request):
    """تحليلات الاستبيانات"""
    surveys = Survey.objects.all()
    total_surveys = surveys.count()
    total_responses = SurveyResponse.objects.count()
    
    # إحصائيات الاستبيانات النشطة
    active_surveys = surveys.filter(status='active')
    active_responses = SurveyResponse.objects.filter(survey__status='active').count()
    
    # معدل الاستجابة
    total_invitations = SurveyInvitation.objects.filter(status='sent').count()
    response_rate = round((total_responses / total_invitations * 100) if total_invitations > 0 else 0, 1)
    
    context = {
        'total_surveys': total_surveys,
        'total_responses': total_responses,
        'active_surveys': active_surveys.count(),
        'active_responses': active_responses,
        'response_rate': response_rate,
    }
    return render(request, 'surveys/survey_analytics.html', context)

@login_required
def survey_templates(request):
    """قوالب الاستبيانات"""
    templates = SurveyTemplate.objects.all()
    return render(request, 'surveys/survey_templates.html', {'templates': templates})

@login_required
@require_http_methods(["GET"])
def api_survey_chart_data(request, pk):
    """API للحصول على بيانات الرسوم البيانية للاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    
    # بيانات الاستجابة عبر الزمن
    responses = survey.responses.all()
    dates = []
    counts = []
    
    for i in range(7):  # آخر 7 أيام
        date = timezone.now().date() - timedelta(days=i)
        count = responses.filter(submitted_at__date=date).count()
        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(count)
    
    data = {
        'dates': list(reversed(dates)),
        'counts': list(reversed(counts)),
        'total_responses': responses.count(),
    }
    
    return JsonResponse(data)

@login_required
def survey_analytics_detail(request, pk):
    """تفاصيل تحليلات الاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    responses = survey.responses.all()
    
    # إحصائيات مفصلة
    total_responses = responses.count()
    questions = survey.questions.all()
    
    # تحليل الإجابات
    question_stats = []
    for question in questions:
        answers = Answer.objects.filter(question=question)
        if question.question_type == 'multiple_choice':
            choice_stats = []
            for choice in question.choices.all():
                count = answers.filter(text_answer=choice.text).count()
                percentage = round((count / total_responses * 100) if total_responses > 0 else 0, 1)
                choice_stats.append({
                    'choice': choice.text,
                    'count': count,
                    'percentage': percentage
                })
            question_stats.append({
                'question': question,
                'type': 'multiple_choice',
                'choices': choice_stats
            })
        else:
            question_stats.append({
                'question': question,
                'type': 'text',
                'answer_count': answers.count()
            })
    
    context = {
        'survey': survey,
        'total_responses': total_responses,
        'question_stats': question_stats,
    }
    return render(request, 'surveys/survey_analytics_detail.html', context)

@login_required
def survey_templates_list(request):
    """قائمة قوالب الاستبيانات"""
    templates = SurveyTemplate.objects.all()
    return render(request, 'surveys/survey_templates_list.html', {'templates': templates})

@login_required
def survey_template_create(request):
    """إنشاء قالب استبيان"""
    if request.method == 'POST':
        form = SurveyTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, 'تم إنشاء القالب بنجاح!')
            return redirect('surveys:templates_list')
    else:
        form = SurveyTemplateForm()
    
    return render(request, 'surveys/survey_template_form.html', {'form': form})

@login_required
def survey_template_edit(request, pk):
    """تعديل قالب استبيان"""
    template = get_object_or_404(SurveyTemplate, pk=pk)
    
    if request.method == 'POST':
        form = SurveyTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث القالب بنجاح!')
            return redirect('surveys:templates_list')
    else:
        form = SurveyTemplateForm(instance=template)
    
    return render(request, 'surveys/survey_template_form.html', {'form': form})

@login_required
def survey_template_delete(request):
    """حذف قالب استبيان"""
    template = get_object_or_404(SurveyTemplate, pk=request.POST.get('template_id'))
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'تم حذف القالب بنجاح!')
    return redirect('surveys:templates_list')

@login_required
def survey_template_preview(request):
    """معاينة قالب استبيان"""
    template = get_object_or_404(SurveyTemplate, pk=request.GET.get('template_id'))
    return render(request, 'surveys/survey_template_preview.html', {'template': template})

@login_required
def question_edit(request, survey_pk, question_pk):
    """تعديل سؤال"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    question = get_object_or_404(Question, pk=question_pk, survey=survey)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث السؤال بنجاح!')
            return redirect('surveys:detail', pk=survey.pk)
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'surveys/question_form.html', {
        'form': form, 
        'survey': survey, 
        'title': 'تعديل السؤال'
    })

@login_required
def question_delete(request, survey_pk, question_pk):
    """حذف سؤال"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    question = get_object_or_404(Question, pk=question_pk, survey=survey)
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'تم حذف السؤال بنجاح!')
        return redirect('surveys:detail', pk=survey.pk)
    
    return render(request, 'surveys/question_confirm_delete.html', {
        'question': question, 
        'survey': survey
    })

@login_required
def choice_create(request, survey_pk, question_pk):
    """إضافة خيار للسؤال"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    question = get_object_or_404(Question, pk=question_pk, survey=survey)
    
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.order = question.choices.count() + 1
            choice.save()
            messages.success(request, 'تم إضافة الخيار بنجاح!')
            return redirect('surveys:detail', pk=survey.pk)
    else:
        form = ChoiceForm()
    
    return render(request, 'surveys/choice_form.html', {
        'form': form, 
        'survey': survey, 
        'question': question,
        'title': 'إضافة خيار جديد'
    })

@login_required
def choice_edit(request, survey_pk, question_pk, choice_pk):
    """تعديل خيار"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    question = get_object_or_404(Question, pk=question_pk, survey=survey)
    choice = get_object_or_404(QuestionChoice, pk=choice_pk, question=question)
    
    if request.method == 'POST':
        form = ChoiceForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الخيار بنجاح!')
            return redirect('surveys:detail', pk=survey.pk)
    else:
        form = ChoiceForm(instance=choice)
    
    return render(request, 'surveys/choice_form.html', {
        'form': form, 
        'survey': survey, 
        'question': question,
        'title': 'تعديل الخيار'
    })

@login_required
def choice_delete(request, survey_pk, question_pk, choice_pk):
    """حذف خيار"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    question = get_object_or_404(Question, pk=question_pk, survey=survey)
    choice = get_object_or_404(QuestionChoice, pk=choice_pk, question=question)
    
    if request.method == 'POST':
        choice.delete()
        messages.success(request, 'تم حذف الخيار بنجاح!')
        return redirect('surveys:detail', pk=survey.pk)
    
    return render(request, 'surveys/choice_confirm_delete.html', {
        'choice': choice, 
        'survey': survey, 
        'question': question
    })

@login_required
def survey_response_list(request, survey_pk):
    """قائمة استجابات الاستبيان"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    responses = survey.responses.all().order_by('-submitted_at')
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        responses = responses.filter(
            Q(respondent_name__icontains=search_query) |
            Q(respondent_email__icontains=search_query)
        )
    
    # التقسيم إلى صفحات
    paginator = Paginator(responses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'survey': survey,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'surveys/survey_response_list.html', context)

@login_required
def create_google_form_survey(request):
    """إنشاء استبيان من Google Forms"""
    if request.method == 'POST':
        google_form_url = request.POST.get('google_form_url')
        if google_form_url:
            # إنشاء استبيان جديد مع رابط Google Forms
            survey = Survey.objects.create(
                title=request.POST.get('title', 'استبيان Google Forms'),
                description=request.POST.get('description', ''),
                google_form_url=google_form_url,
                created_by=request.user,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30)
            )
            messages.success(request, 'تم إنشاء الاستبيان بنجاح!')
            return redirect('surveys:detail', pk=survey.pk)
    
    return render(request, 'surveys/create_google_form_survey.html')

def export_survey_responses(survey, surveyresponses, format_type):
    """تصدير استجابات الاستبيان"""
    if format_type == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="survey_{survey.id}_responses.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['السؤال', 'الإجابة', 'المستجيب', 'التاريخ'])
        
        for survey_response in surveyresponses:
            for answer in survey_response.answers.all():
                writer.writerow([
                    answer.question.question_text,
                    answer.text_answer,
                    survey_response.respondent_name,
                    survey_response.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        return response
    
    elif format_type == 'pdf':
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="survey_{survey.id}_responses.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        p.drawString(100, 750, f'نتائج الاستبيان: {survey.title}')
        
        y = 700
        for survey_response in surveyresponses:
            p.drawString(100, y, f'المستجيب: {survey_response.respondent_name}')
            y -= 20
            for answer in survey_response.answers.all():
                p.drawString(120, y, f'{answer.question.question_text}: {answer.text_answer}')
                y -= 15
            y -= 20
        
        p.showPage()
        p.save()
        return response

@login_required
def bulk_delete_responses(request):
    """حذف جماعي للاستجابات"""
    if request.method == 'POST':
        response_ids = request.POST.getlist('response_ids')
        SurveyResponse.objects.filter(id__in=response_ids).delete()
        messages.success(request, f'تم حذف {len(response_ids)} استجابة بنجاح!')
    return redirect('surveys:list')

@login_required
def delete_response(request):
    """حذف استجابة واحدة"""
    if request.method == 'POST':
        response_id = request.POST.get('response_id')
        response = get_object_or_404(SurveyResponse, id=response_id)
        response.delete()
        messages.success(request, 'تم حذف الاستجابة بنجاح!')
    return redirect('surveys:list')

@login_required
def get_graduates(request):
    """API للحصول على قائمة الخريجين"""
    college = request.GET.get('college')
    graduates = Graduate.objects.filter(is_active=True)
    
    if college:
        graduates = graduates.filter(college__icontains=college)
    
    data = [{'id': g.id, 'name': g.full_name, 'email': g.email} for g in graduates]
def send_survey_bulk(request):
    """إرسال جماعي للاستبيانات"""
    if request.method == 'POST':
        survey_id = request.POST.get('survey_id')
        graduate_ids = request.POST.getlist('graduate_ids')
        
        survey = get_object_or_404(Survey, id=survey_id)
        graduates = Graduate.objects.filter(id__in=graduate_ids)
        
        success_count = 0
        fail_count = 0

        for graduate in graduates:
            if graduate.email:
                try:
                    # Create a unique invitation token
                    invitation, created = SurveyInvitation.objects.get_or_create(
                        survey=survey,
                        graduate=graduate,
                        defaults={'token': secrets.token_urlsafe(20)}
                    )

                    # Generate the survey link
                    survey_link = request.build_absolute_uri(
                        reverse('surveys:take_survey_by_token', kwargs={'token': invitation.token})
                    )

                    # Email subject and content
                    subject = f'دعوة للمشاركة في استبيان: {survey.title}'
                    html_message = render_to_string('surveys/survey_email_template.html', {
                        'survey_title': survey.title,
                        'graduate_name': graduate.full_name,
                        'survey_link': survey_link,
                        'survey_description': survey.description
                    })
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [graduate.email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    invitation.status = 'sent'
                    invitation.sent_at = timezone.now()
                    invitation.save()
                    success_count += 1
                    SurveySendLog.objects.create(survey=survey, graduate=graduate, status='success', channel='email')
                except Exception as e:
                    fail_count += 1
                    SurveySendLog.objects.create(survey=survey, graduate=graduate, status='failed', channel='email', details=str(e))
            else:
                fail_count += 1
                SurveySendLog.objects.create(survey=survey, graduate=graduate, status='failed', channel='email', details='No email address')

        if success_count > 0:
            messages.success(request, f'تم إرسال الاستبيان بنجاح إلى {success_count} خريج عبر البريد الإلكتروني.')
        if fail_count > 0:
            messages.warning(request, f'فشل إرسال الاستبيان إلى {fail_count} خريج لعدم وجود بريد إلكتروني أو خطأ في الإرسال.')

        return redirect('surveys:detail', pk=survey.pk)
    
    surveys = Survey.objects.filter(status='active')
    graduates = Graduate.objects.filter(is_active=True)
    
    return render(request, 'surveys/send_survey_bulk.html', {
        'surveys': surveys,
        'graduates': graduates
    })

@login_required
def send_survey_logs(request, survey_id):
    """سجلات إرسال الاستبيان"""
    survey = get_object_or_404(Survey, pk=survey_id)
    logs = SurveySendLog.objects.filter(survey=survey).order_by('-sent_at')
    
    return render(request, 'surveys/send_survey_logs.html', {
        'survey': survey,
        'logs': logs
    })

def take_survey_public(request, pk):
    """ملء الاستبيان للعامة (بدون تسجيل دخول)"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        # حفظ الاستجابة
        response = SurveyResponse.objects.create(
            survey=survey,
            respondent_name=request.POST.get('respondent_name', ''),
            respondent_email=request.POST.get('respondent_email', ''),
            submitted_at=timezone.now()
        )
        
        # حفظ الإجابات
        for question in survey.questions.all():
            answer_text = request.POST.get(f'question_{question.id}')
            if answer_text:
                Answer.objects.create(
                    response=response,
                    question=question,
                    text_answer=answer_text
                )
        
        messages.success(request, 'تم إرسال الاستبيان بنجاح!')
        return redirect('surveys:thank_you_public', pk=survey.pk)
    
    return render(request, 'surveys/take_survey_public.html', {'survey': survey})

def survey_thank_you_public(request, pk):
    """صفحة شكر للعامة"""
    survey = get_object_or_404(Survey, pk=pk)
    return render(request, 'surveys/survey_thank_you_public.html', {'survey': survey})

@login_required
def survey_templates_select(request):
    """اختيار قالب استبيان"""
    templates = SurveyTemplate.objects.all()
    return render(request, 'surveys/survey_templates_select.html', {'templates': templates})

@login_required
def survey_create_from_template(request, template_id):
    """إنشاء استبيان من قالب"""
    template = get_object_or_404(SurveyTemplate, pk=template_id)
    
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.template_name = template.title
            survey.save()
            
            # نسخ الأسئلة من القالب (إذا كانت موجودة)
            # يمكن إضافة منطق نسخ الأسئلة هنا
            
            messages.success(request, 'تم إنشاء الاستبيان من القالب بنجاح!')
            return redirect('surveys:detail', pk=survey.pk)
    else:
        form = SurveyForm(initial={'title': template.title, 'description': template.description})
    
    return render(request, 'surveys/survey_form.html', {
        'form': form, 
        'template': template,
        'title': f'إنشاء استبيان من قالب: {template.title}'
    }) 

# ===== النظام الجديد المبسط للاستبيانات =====

@login_required
def new_surveys_home(request):
    """الصفحة الرئيسية الجديدة للاستبيانات"""
    surveys = Survey.objects.all().order_by('-created_at')[:10]
    total_surveys = Survey.objects.count()
    active_surveys = Survey.objects.filter(status='active').count()
    
    context = {
        'surveys': surveys,
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
    }
    return render(request, 'surveys/new_surveys_home.html', context)

@login_required
def new_survey_create(request):
    """إنشاء استبيان جديد مبسط مع دعم الحقول الجديدة والأسئلة الديناميكية"""
    if request.method == 'POST':
        form = NewSurveyForm(request.POST, request.FILES)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.status = 'draft'
            from django.utils import timezone
            from datetime import timedelta
            survey.start_date = timezone.now()
            survey.end_date = timezone.now() + timedelta(days=30)
            survey.save()
            # حفظ الأسئلة الديناميكية
            questions_data = request.POST.getlist('questions[]')
            for qdata in questions_data:
                import json
                qobj = json.loads(qdata)
                question = Question.objects.create(
                    survey=survey,
                    question_text=qobj['text'],
                    question_type=qobj['type'],
                    order=int(qobj['order']) if qobj.get('order') else 0,
                    is_required=True
                )
                # إذا كان هناك خيارات
                if qobj['type'] in ['radio', 'checkbox', 'select'] and qobj.get('choices'):
                    choices = [c.strip() for c in qobj['choices'].split('\n') if c.strip()]
                    for i, choice_text in enumerate(choices):
                        QuestionChoice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            order=i+1
                        )
            messages.success(request, 'تم إنشاء الاستبيان بنجاح!')
            return redirect('surveys:new_survey_success')
    else:
        form = NewSurveyForm()
    return render(request, 'surveys/new_survey_create.html', {'form': form, 'title': 'إنشاء استبيان جديد'})

@login_required
def new_survey_created(request):
    """صفحة نجاح إنشاء الاستبيان"""
    latest_survey = Survey.objects.filter(created_by=request.user).order_by('-created_at').first()
    return render(request, 'surveys/new_survey_created.html', {
        'survey': latest_survey
    })

@login_required
def new_survey_list(request):
    """قائمة الاستبيانات (واجهة جديدة)"""
    surveys = Survey.objects.all().order_by('-created_at')
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        surveys = surveys.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    # الفلترة حسب الحالة
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        surveys = surveys.filter(is_active=True)
    elif status_filter == 'inactive':
        surveys = surveys.filter(is_active=False)
    # التقسيم إلى صفحات
    paginator = Paginator(surveys, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'surveys/survey_list.html', context)

@login_required
def new_survey_detail(request, pk):
    """تفاصيل الاستبيان الجديد"""
    survey = get_object_or_404(Survey, pk=pk)
    questions = survey.questions.all().order_by('order')
    
    context = {
        'survey': survey,
        'questions': questions,
    }
    return render(request, 'surveys/new_survey_detail.html', context)

@login_required
def new_question_add(request, survey_pk):
    """إضافة سؤال جديد للاستبيان"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    
    if request.method == 'POST':
        form = NewQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.question_type = 'radio'  # نوع ثابت: اختيار من متعدد
            question.is_required = True
            question.order = survey.questions.count() + 1
            question.save()
            
            # إضافة الخيارات
            choices_text = form.cleaned_data.get('choices', '')
            choices = [choice.strip() for choice in choices_text.split('\n') if choice.strip()]
            
            for i, choice_text in enumerate(choices):
                QuestionChoice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    order=i + 1
                )
            
            messages.success(request, 'تم إضافة السؤال بنجاح!')
            return redirect('surveys:question_added', survey_pk=survey.pk)
    else:
        form = NewQuestionForm()
    
    return render(request, 'surveys/new_question_add.html', {
        'form': form,
        'survey': survey,
        'title': 'إضافة سؤال جديد'
    })

@login_required
def new_question_added(request, survey_pk):
    """صفحة نجاح إضافة السؤال"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    latest_question = survey.questions.order_by('-order').first()
    
    return render(request, 'surveys/new_question_added.html', {
        'survey': survey,
        'question': latest_question
    })

@login_required
def new_question_delete(request, survey_pk, question_pk):
    """حذف سؤال من الاستبيان"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    question = get_object_or_404(Question, pk=question_pk, survey=survey)
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'تم حذف السؤال بنجاح!')
        return redirect('surveys:detail', pk=survey.pk)
    
    return render(request, 'surveys/new_question_delete_confirm.html', {
        'survey': survey,
        'question': question
    })

@login_required
def new_survey_send(request, pk):
    """إرسال الاستبيان للخريجين"""
    survey = get_object_or_404(Survey, pk=pk)
    graduates = Graduate.objects.filter(is_active=True)
    
    if request.method == 'POST':
        selected_graduates = request.POST.getlist('graduates')
        if selected_graduates:
            selected_graduates = Graduate.objects.filter(id__in=selected_graduates)
            
            # إرسال الاستبيان
            sender = SurveySender()
            successful_sends, failed_sends = sender.send_invitations(survey, selected_graduates, request)
            
            if len(successful_sends) > 0:
                messages.success(request, f'تم إرسال الاستبيان إلى {len(successful_sends)} خريج بنجاح!')

            if len(failed_sends) > 0:
                messages.warning(request, f'فشل في إرسال الاستبيان إلى {len(failed_sends)} خريج.')
            
            return redirect('surveys:detail', pk=survey.pk)
        else:
            messages.error(request, 'يرجى اختيار خريجين على الأقل.')
    
    return render(request, 'surveys/new_survey_send.html', {
        'survey': survey,
        'graduates': graduates
    })

def new_take_survey(request, pk):
    """أخذ الاستبيان (للخريجين)"""
    survey = get_object_or_404(Survey, pk=pk)
    questions = survey.questions.all().order_by('order')
    
    if request.method == 'POST':
        # معالجة الإجابات
        response = SurveyResponse.objects.create(
            survey=survey,
            graduate=None,  # للاستبيانات العامة
            is_complete=True
        )
        
        for question in questions:
            answer_text = request.POST.get(f'question_{question.id}')
            if answer_text:
                Answer.objects.create(
                    response=response,
                    question=question,
                    answer_text=answer_text
                )
        
        return redirect('surveys:submit', pk=survey.pk)
    
    return render(request, 'surveys/new_take_survey.html', {
        'survey': survey,
        'questions': questions
    })

def new_submit_survey(request, pk):
    """معالجة إرسال الاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    return redirect('surveys:thank_you', pk=survey.pk)

def new_survey_thank_you(request, pk):
    """صفحة شكر بعد إكمال الاستبيان"""
    survey = get_object_or_404(Survey, pk=pk)
    return render(request, 'surveys/new_survey_thank_you.html', {
        'survey': survey
    }) 

@login_required
def new_survey_success(request):
    """صفحة نجاح احتفالية بعد إنشاء الاستبيان"""
    return render(request, 'surveys/new_survey_success.html')

@login_required
def edit_select(request):
    """اختيار استبيان للتعديل (واجهة مؤقتة)"""
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'surveys/edit_select.html', {'surveys': surveys}) 

@login_required
def delete_select(request):
    """اختيار استبيان للحذف (واجهة مؤقتة)"""
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'surveys/delete_select.html', {'surveys': surveys}) 

@login_required
def send_select(request):
    """اختيار استبيان للإرسال (واجهة مؤقتة)"""
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'surveys/send_select.html', {'surveys': surveys}) 

@login_required
def view_survey(request, pk):
    """عرض الاستبيان فقط بشكل جمالي وجذاب بدون أزرار تحكم"""
    survey = get_object_or_404(Survey, pk=pk)
    questions = survey.questions.all().order_by('order')
    return render(request, 'surveys/view_survey.html', {
        'survey': survey,
        'questions': questions
    }) 