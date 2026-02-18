from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    User, Announcement, Course, Survey, TalentedStudentDatabase,
    StateScholarship, BuxduScholarship, BuxduWinnerDatabase,
    Olympiad, BuxduOlympiadWinner, BuxduOlympiad, BuxduOlympiadImage, OakDatabase,
    Conference, DissertationBank, ArticleBank, ResearcherRegulation,
    Module, Question, Answer, UserCourseProgress,
    UserModuleProgress, UserTestResult, Certificate, TestSet,
    AssessmentTest, AssessmentTestResult
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'residence_region', 'university', 'academic_degree', 'status', 'assessment_status')
    list_filter = ('status', 'academic_degree', 'assessment_status', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'university')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {'fields': ('phone_number', 'residence_region', 'university', 'academic_degree', 'status', 'profile_image')}),
        ('Saralash testi', {'fields': ('assessment_status', 'assessment_score', 'assessment_taken_at', 'assessment_next_attempt')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {'fields': ('phone_number', 'residence_region', 'university', 'academic_degree', 'status')}),
    )
    readonly_fields = ('assessment_taken_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    from main.forms import AnnouncementAdminForm
    form = AnnouncementAdminForm
    list_display = ('title', 'author', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title', 'short_text', 'author')
    date_hierarchy = 'date'
    fields = ('author', 'title', 'date', 'short_text', 'detailed_text', 'image', 'image_url')


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ('number', 'name', 'description', 'youtube_url', 'presentation')
    readonly_fields = ('number',)
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


# Test to'plamlari admin
@admin.register(TestSet)
class TestSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('question_count', 'created_at', 'updated_at')
    fields = ('name', 'description', 'question_count', 'created_at', 'updated_at')
    
    def question_count(self, obj):
        if obj.pk:
            return obj.questions.count()
        return 0
    question_count.short_description = 'Savollar soni'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    from main.forms import CourseAdminForm
    form = CourseAdminForm
    list_display = ('name', 'module_count', 'test_set', 'passing_score', 'is_active', 'created_at')
    search_fields = ('name', 'short_description')
    list_filter = ('is_active', 'test_set', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ModuleInline]
    fields = ('name', 'short_description', 'image', 'is_active', 'module_count', 'test_set', 'time_per_question', 'passing_score', 'created_at', 'updated_at')


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    from main.forms import SurveyAdminForm
    form = SurveyAdminForm
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    fields = ('title', 'description', 'link', 'is_active')


@admin.register(TalentedStudentDatabase)
class TalentedStudentDatabaseAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'file_name', 'file_format', 'created_at')
    list_filter = ('file_format', 'created_at')
    search_fields = ('academic_year', 'file_name')
    fields = ('academic_year', 'file_name', 'file_format', 'file')


@admin.register(StateScholarship)
class StateScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'short_description')
    fields = ('name', 'short_description', 'regulation_link', 'application_link')


@admin.register(BuxduScholarship)
class BuxduScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'short_description')
    fields = ('name', 'short_description', 'regulation_file', 'application_link')


@admin.register(BuxduWinnerDatabase)
class BuxduWinnerDatabaseAdmin(admin.ModelAdmin):
    list_display = ('scholarship_type', 'academic_year', 'file_name', 'created_at')
    list_filter = ('academic_year', 'scholarship_type')
    search_fields = ('scholarship_type', 'file_name')
    fields = ('academic_year', 'scholarship_type', 'file_name', 'file')


@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    from main.forms import OlympiadAdminForm
    form = OlympiadAdminForm
    list_display = ('name', 'subject', 'country', 'type', 'created_at')
    list_filter = ('subject', 'country', 'type')
    search_fields = ('name', 'subject', 'country')
    fields = ('type', 'name', 'subject', 'country', 'short_description', 'information_letter', 'registration_link')


@admin.register(BuxduOlympiadWinner)
class BuxduOlympiadWinnerAdmin(admin.ModelAdmin):
    list_display = ('olympiad_name', 'subject', 'academic_year', 'created_at')
    list_filter = ('academic_year', 'subject')
    search_fields = ('olympiad_name', 'subject')
    fields = ('olympiad_name', 'subject', 'academic_year', 'file_name', 'file')


# Inline for BuxduOlympiad images
class BuxduOlympiadImageInline(admin.TabularInline):
    model = BuxduOlympiadImage
    extra = 1
    fields = ('image', 'caption')
    verbose_name = 'Olimpiada rasmi'
    verbose_name_plural = 'Olimpiada rasmlari'


@admin.register(BuxduOlympiad)
class BuxduOlympiadAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date', 'status_display', 'image_count', 'created_at')
    list_filter = ('date', 'subject')
    search_fields = ('subject', 'description')
    date_hierarchy = 'date'
    readonly_fields = ('status_display', 'image_count')
    inlines = [BuxduOlympiadImageInline]
    fields = ('subject', 'date', 'status_display', 'description', 'image', 'program_file', 
              'registration_link_1', 'registration_link_2', 'result_file')
    
    def status_display(self, obj):
        """Status ko'rsatish"""
        if obj.is_finished:
            return mark_safe('<span style="color: #dc2626; font-weight: bold;">🔴 Tugagan</span>')
        return mark_safe('<span style="color: #16a34a; font-weight: bold;">🟢 Kutilmoqda</span>')
    status_display.short_description = 'Status'
    
    def image_count(self, obj):
        """Yuklangan rasmlar soni"""
        if obj.pk:
            count = obj.images.count()
            return f"{count} ta rasm"
        return "0 ta rasm"
    image_count.short_description = 'Rasmlar'


@admin.register(OakDatabase)
class OakDatabaseAdmin(admin.ModelAdmin):
    list_display = ('journal_name', 'type', 'created_at')
    list_filter = ('type',)
    search_fields = ('journal_name', 'fields')
    fields = ('type', 'journal_name', 'fields', 'database_link', 'editorial_link')


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at')
    list_filter = ('type',)
    search_fields = ('name',)
    fields = ('type', 'name', 'information_letter', 'organizer_link')


@admin.register(DissertationBank)
class DissertationBankAdmin(admin.ModelAdmin):
    list_display = ('database_type', 'direction', 'created_at')
    list_filter = ('database_type',)
    search_fields = ('database_type', 'direction')
    fields = ('database_type', 'direction', 'link')


@admin.register(ArticleBank)
class ArticleBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'short_guide')
    fields = ('name', 'short_guide', 'database_link')


@admin.register(ResearcherRegulation)
class ResearcherRegulationAdmin(admin.ModelAdmin):
    list_display = ('regulation_name', 'created_at')
    search_fields = ('regulation_name',)
    fields = ('regulation_name', 'file')


# Savollar admin (to'liq funksional)
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    from main.forms import QuestionWithAnswersForm
    form = QuestionWithAnswersForm
    
    list_display = ('test_set', 'number', 'text_preview', 'answer_count')
    list_filter = ('test_set',)
    search_fields = ('text',)
    ordering = ('test_set', 'number')
    readonly_fields = ('created_at', 'answer_preview')
    fields = ('test_set', 'number', 'text', 'answer_a', 'answer_b', 'answer_c', 'answer_d', 'correct_answer', 'answer_preview', 'created_at')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Savol matni'
    
    def answer_count(self, obj):
        if obj.pk:
            return obj.answers.count()
        return 0
    answer_count.short_description = 'Javoblar soni'
    
    def answer_preview(self, obj):
        if not obj.pk:
            return '-'
        answers = obj.answers.all()
        html = '<ul style="list-style: none; padding: 0;">'
        for ans in answers:
            icon = '✓' if ans.is_correct else '○'
            color = 'green' if ans.is_correct else 'black'
            html += f'<li style="color: {color}; padding: 4px 0;">{icon} {ans.text}</li>'
        html += '</ul>'
        from django.utils.safestring import mark_safe
        return mark_safe(html)
    answer_preview.short_description = 'Javoblar ko\'rinishi'
    
    def save_model(self, request, obj, form, change):
        """Save the instance and create answers"""
        from .models import Answer
        
        # Save the question first
        super().save_model(request, obj, form, change)
        
        # Now create/update answers
        # Delete old answers
        obj.answers.all().delete()
        
        # Create new answers from form data
        answers_data = [
            ('A', form.cleaned_data.get('answer_a')),
            ('B', form.cleaned_data.get('answer_b')),
            ('C', form.cleaned_data.get('answer_c')),
            ('D', form.cleaned_data.get('answer_d')),
        ]
        
        correct = form.cleaned_data.get('correct_answer')
        
        for letter, text in answers_data:
            if text:  # Only create if text is provided
                Answer.objects.create(
                    question=obj,
                    text=text,
                    is_correct=(letter == correct)
                )
        
        print(f"DEBUG: Created {obj.answers.count()} answers for question {obj.number}")


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_completed', 'test_passed', 'test_score', 'started_at')
    list_filter = ('is_completed', 'test_passed', 'course')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'course__name')
    readonly_fields = ('started_at', 'completed_at')


@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'viewed_presentation', 'watched_video', 'is_completed')
    list_filter = ('is_completed', 'module__course')
    search_fields = ('user__email', 'module__name')
    readonly_fields = ('completed_at',)


@admin.register(UserTestResult)
class UserTestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'percentage', 'passed', 'submitted_at')
    list_filter = ('passed', 'course')
    search_fields = ('user__email', 'course__name')
    readonly_fields = ('submitted_at',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'issued_at', 'download_link')
    list_filter = ('course', 'issued_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'course__name')
    readonly_fields = ('user', 'course', 'test_result', 'issued_at', 'download_link')
    
    def download_link(self, obj):
        if obj.certificate_file:
            return format_html('<a href="{}" target="_blank">Yuklab olish</a>', obj.certificate_file.url)
        return '-'
    download_link.short_description = 'Sertifikat'


# Saralash testi admin
@admin.register(AssessmentTest)
class AssessmentTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'test_set', 'time_limit', 'pass_percentage', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('title', 'description', 'test_set', 'is_active', 'time_limit', 'pass_percentage', 'retry_delay_hours', 'created_at', 'updated_at')


@admin.register(AssessmentTestResult)
class AssessmentTestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment_test', 'percentage', 'passed', 'correct_answers', 'total_questions', 'submitted_at')
    list_filter = ('passed', 'assessment_test', 'submitted_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'assessment_test', 'score', 'total_questions', 'correct_answers', 
                      'percentage', 'passed', 'time_taken', 'submitted_at')
    date_hierarchy = 'submitted_at'
    
    def has_add_permission(self, request):
        return False

