import secrets
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.urls import reverse
from django.contrib.sites.models import Site
from graduate_system import settings
from .models import SurveyInvitation, SurveySendLog

class SurveySender:
    def send_invitations(self, survey, graduates, request):
        """
        Sends survey invitations to a list of graduates and logs the process.
        Returns a tuple of (successful_sends, failed_sends) lists.
        """
        successful_sends = []
        failed_sends = []

        for graduate in graduates:
            while True:
                token = secrets.token_urlsafe(16)
                if not SurveyInvitation.objects.filter(invitation_token=token).exists():
                    break

            invitation, created = SurveyInvitation.objects.get_or_create(
                survey=survey,
                graduate=graduate
            )

            # إذا كانت الدعوة موجودة مسبقًا ولكن بدون رمز، أو إذا كانت جديدة، قم بإنشاء رمز
            if created or not invitation.invitation_token:
                invitation.invitation_token = token
                invitation.status = 'pending' # إعادة تعيين الحالة عند إعادة الإرسال
                invitation.save()

            # إرسال البريد الإلكتروني فقط إذا تم إنشاء الدعوة حديثًا أو إذا أردنا إعادة الإرسال دائمًا
            # في الوقت الحالي، سنقوم بالإرسال في كل مرة يتم فيها تحديد الخريج

            # بناء رابط الاستبيان باستخدام Django Sites Framework
            current_site = Site.objects.get_current()
            survey_path = reverse('surveys:take_survey_by_token', args=[invitation.invitation_token])
            survey_url = f'http://{current_site.domain}{survey_path}'

            # Prepare email content
            subject = f'دعوة للمشاركة في استبيان: {survey.title}'
            context = {
                'graduate_name': graduate.full_name,
                'survey_title': survey.title,
                'survey_link': survey_url,  # تصحيح اسم المتغير ليتطابق مع القالب
            }
            html_message = render_to_string('surveys/survey_email_template.html', context)
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = graduate.email

            try:
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
                SurveySendLog.objects.create(
                    survey=survey,
                    graduate=graduate,
                    status='success',
                    details=f'Email sent successfully to {to_email}'
                )
                successful_sends.append(graduate)
            except Exception as e:
                SurveySendLog.objects.create(
                    survey=survey,
                    graduate=graduate,
                    status='failed',
                    error_message=f'Failed to send email to {to_email}: {str(e)}'
                )
                failed_sends.append((graduate, str(e)))
        
        return successful_sends, failed_sends
