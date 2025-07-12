from django.contrib import admin
from .models import Survey, Question, QuestionChoice, SurveyResponse, Answer, SurveyInvitation


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 3


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'created_by', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات الاستبيان', {
            'fields': ('title', 'description', 'status')
        }),
        ('التوقيت', {
            'fields': ('start_date', 'end_date')
        }),
        ('معلومات النظام', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_preview', 'survey', 'question_type', 'is_required', 'order']
    list_filter = ['question_type', 'is_required', 'survey']
    search_fields = ['question_text', 'survey__title']
    inlines = [QuestionChoiceInline]
    
    def question_text_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = 'نص السؤال'


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'order']
    list_filter = ['question__survey', 'question__question_type']
    search_fields = ['choice_text', 'question__question_text']


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['graduate', 'survey', 'is_complete', 'submitted_at']
    list_filter = ['is_complete', 'survey', 'submitted_at']
    search_fields = ['graduate__first_name', 'graduate__last_name', 'survey__title']
    readonly_fields = ['submitted_at']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['response', 'question', 'answer_preview']
    list_filter = ['question__question_type', 'response__survey']
    search_fields = ['response__graduate__first_name', 'response__graduate__last_name', 'question__question_text']
    
    def answer_preview(self, obj):
        if obj.answer_text:
            return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
        elif obj.answer_number:
            return str(obj.answer_number)
        elif obj.answer_date:
            return str(obj.answer_date)
        elif obj.selected_choices.exists():
            return ', '.join([choice.choice_text for choice in obj.selected_choices.all()])
        return 'لا توجد إجابة'
    answer_preview.short_description = 'الإجابة'


@admin.register(SurveyInvitation)
class SurveyInvitationAdmin(admin.ModelAdmin):
    list_display = ['graduate', 'survey', 'status', 'sent_at', 'completed_at']
    list_filter = ['status', 'survey', 'sent_at']
    search_fields = ['graduate__first_name', 'graduate__last_name', 'survey__title']
    readonly_fields = ['invitation_token', 'sent_at', 'opened_at', 'completed_at', 'created_at']

