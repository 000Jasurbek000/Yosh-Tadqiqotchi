from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import path
from .models import (
    User, Announcement, Course, Survey, TalentedStudentDatabase,
    StateScholarship, BuxduScholarship, BuxduWinnerDatabase,
    Olympiad, BuxduOlympiadWinner, BuxduOlympiad, BuxduOlympiadImage, OakDatabase,
    Conference, DissertationBank, ArticleBank, ResearcherRegulation,
    Module, Question, Answer, UserCourseProgress,
    UserModuleProgress, UserTestResult, Certificate, TestSet,
    AssessmentTest, AssessmentTestResult, Literature, ScientificSupervisor,
    SupervisorRequest, OlympiadProgram, OlympiadApplication
)
from . import admin_db
from . import admin_stats
from .utils_display import format_assessment_status


# Admin URL larga "Baza boshqaruvi" va "Statistika" sahifalarini qo'shamiz
_original_get_urls = admin.site.get_urls


def _custom_get_urls():
    from . import admin_olympiad
    custom_urls = [
        path('database/download/', admin.site.admin_view(admin_db.download_db), name='db_download'),
        path('database/upload/',   admin.site.admin_view(admin_db.upload_db),   name='db_upload'),
        path('database/clear/',    admin.site.admin_view(admin_db.clear_db),    name='db_clear'),
        path('statistics/',         admin.site.admin_view(admin_stats.statistics_view),  name='statistics'),
        path('statistics/excel/',   admin.site.admin_view(admin_stats.statistics_excel), name='statistics_excel'),
        path('olympiad-applications/excel/', admin.site.admin_view(admin_olympiad.olympiad_applications_excel), name='olympiad_applications_excel'),
    ]
    return custom_urls + _original_get_urls()


admin.site.get_urls = _custom_get_urls
admin.site.site_header = "Yosh Tadqiqotchi — Admin panel"
admin.site.site_title = "Yosh Tadqiqotchi"
admin.site.index_title = "Boshqaruv paneli"


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
    list_display = ('name', 'regulation_source', 'created_at')
    search_fields = ('name', 'short_description')
    fieldsets = (
        (None, {
            'fields': ('name', 'short_description'),
        }),
        ('Nizom', {
            'fields': ('regulation_link', 'regulation_file'),
            'description': 'Havola yoki PDF fayldan birini kiriting. Tashqi havola tavsiya etiladi.',
        }),
        ('Ariza', {
            'fields': ('application_link',),
            'description': 'OTM bosqichida ariza topshirish uchun havola.',
        }),
    )

    @admin.display(description='Nizom')
    def regulation_source(self, obj):
        if obj.regulation_link:
            return 'Havola'
        if obj.regulation_file:
            return 'Fayl'
        return '—'


@admin.register(BuxduScholarship)
class BuxduScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'regulation_source', 'created_at')
    search_fields = ('name', 'short_description')
    fieldsets = (
        (None, {
            'fields': ('name', 'short_description'),
        }),
        ('Nizom', {
            'fields': ('regulation_link', 'regulation_file'),
            'description': 'Havola yoki PDF fayldan birini kiriting. Tashqi havola tavsiya etiladi.',
        }),
        ('Ariza', {
            'fields': ('application_link',),
            'description': 'Onlayn ariza topshirish uchun havola.',
        }),
    )

    @admin.display(description='Nizom')
    def regulation_source(self, obj):
        if obj.regulation_link:
            return 'Havola'
        if obj.regulation_file:
            return 'Fayl'
        return '—'


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
    list_display = ('name', 'subject', 'country', 'type', 'date', 'created_at')
    list_filter = ('subject', 'country', 'type', 'date')
    search_fields = ('name', 'subject', 'country')
    fields = ('type', 'name', 'subject', 'country', 'date', 'short_description', 'image', 'information_letter', 'registration_link')


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
    list_display = ('name', 'type', 'letter_source', 'created_at')
    list_filter = ('type',)
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('type', 'name', 'organizer_link'),
        }),
        ('Axborot xati', {
            'fields': ('information_letter_link', 'information_letter'),
            'description': 'Havola yoki PDF fayldan birini kiriting. Tashqi havola tavsiya etiladi.',
        }),
    )

    @admin.display(description='Axborot xati')
    def letter_source(self, obj):
        if obj.information_letter_link:
            return 'Havola'
        if obj.information_letter:
            return 'Fayl'
        return '—'


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
    list_display = ('regulation_name', 'source_type', 'created_at')
    search_fields = ('regulation_name',)
    fieldsets = (
        (None, {
            'fields': ('regulation_name',),
        }),
        ('Manba', {
            'fields': ('regulation_link', 'file'),
            'description': 'Havola yoki fayldan birini kiriting. Tashqi sayt havolasi tavsiya etiladi.',
        }),
    )

    @admin.display(description='Manba')
    def source_type(self, obj):
        if obj.regulation_link:
            return 'Havola'
        if obj.file:
            return 'Fayl'
        return '—'


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


@admin.register(Literature)
class LiteratureAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'field', 'has_file', 'has_url', 'cover_preview', 'created_at')
    list_filter = ('field', 'created_at')
    search_fields = ('title', 'author', 'description')
    readonly_fields = ('cover_preview', 'created_at', 'updated_at')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'author', 'field', 'description')
        }),
        ('Manba', {
            'fields': ('file', 'url'),
            'description': 'Fayl yoki Internet manzilidan birini kiriting.'
        }),
        ('Muqova rasmi', {
            'fields': ('cover_image', 'cover_preview')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;">', obj.cover_image.url)
        return '—'
    cover_preview.short_description = 'Muqova'

    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
    has_file.short_description = 'Fayl'

    def has_url(self, obj):
        return bool(obj.url)
    has_url.boolean = True
    has_url.short_description = 'URL'


@admin.register(ScientificSupervisor)
class ScientificSupervisorAdmin(admin.ModelAdmin):
    list_display = ('order', 'full_name', 'position', 'specialty', 'phone', 'email',
                    'photo_preview', 'capacity_display', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('full_name', 'position', 'specialty', 'email', 'phone')
    list_editable = ('is_active',)
    readonly_fields = ('photo_preview', 'created_at', 'capacity_display')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('full_name', 'position', 'specialty', 'photo', 'photo_preview')
        }),
        ('Aloqa', {
            'fields': ('phone', 'email')
        }),
        ('Sig\'im (talabalar soni)', {
            'fields': ('max_students', 'capacity_display'),
            'description': 'Bu rahbar qabul qila oladigan eng ko\'p talabalar soni.'
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active', 'created_at')
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:60px;border-radius:50%;">', obj.photo.url)
        return '—'
    photo_preview.short_description = 'Rasm'

    def capacity_display(self, obj):
        if not obj.pk:
            return '—'
        accepted = obj.accepted_count
        total = obj.max_students
        color = '#10b981' if accepted < total else '#ef4444'
        return format_html(
            '<span style="color:{};font-weight:700;">{}/{}</span>',
            color, accepted, total
        )
    capacity_display.short_description = 'Qabul qilingan / Maks.'


@admin.register(SupervisorRequest)
class SupervisorRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'supervisor', 'status_badge', 'created_at', 'decided_at')
    list_filter = ('status', 'supervisor', 'created_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name',
                     'supervisor__full_name')
    readonly_fields = ('token', 'created_at', 'decided_at')
    date_hierarchy = 'created_at'
    fields = ('student', 'supervisor', 'status', 'decision_reason',
              'token', 'created_at', 'decided_at')

    def status_badge(self, obj):
        colors = {'pending': '#f59e0b', 'accepted': '#10b981', 'rejected': '#ef4444'}
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.get_status_display()
        )
    status_badge.short_description = 'Holat'


# ───────────────────────────── Olimpiada dasturi ─────────────────────────────
@admin.register(OlympiadProgram)
class OlympiadProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'applications_count', 'has_task_file', 'is_active', 'updated_at')
    list_filter  = ('is_active', 'code')
    search_fields = ('title', 'short_intro', 'required_skills', 'knowledge_areas')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'applications_count')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('code', 'title', 'short_intro', 'is_active')
        }),
        ('Talab va ko\'nikmalar', {
            'fields': ('required_skills', 'knowledge_areas', 'self_check_text'),
            'description': 'Bu olimpiadaga arizachilar uchun kerakli bilim va ko\'nikmalar'
        }),
        ('Topshiriqlar fayli', {
            'fields': ('task_file',),
            'description': 'PDF, Word yoki boshqa formatdagi topshiriqlar to\'plamini yuklang'
        }),
        ('Qo\'shimcha', {
            'fields': ('additional_info', 'applications_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def applications_count(self, obj):
        if not obj.pk:
            return 0
        return obj.applications.count()
    applications_count.short_description = 'Arizalar soni'

    def has_task_file(self, obj):
        return bool(obj.task_file)
    has_task_file.boolean = True
    has_task_file.short_description = 'Fayl bor'


# ───────────────────────────── Olimpiada arizalari ─────────────────────────────
@admin.register(OlympiadApplication)
class OlympiadApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'application_target', 'application_type', 'status_badge', 'created_at')
    list_filter  = ('status', 'application_type', 'olympiad', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name',
                     'user__phone_number', 'olympiad__title', 'motivation')
    readonly_fields = ('user', 'application_type', 'olympiad', 'motivation', 'created_at', 'updated_at',
                       'user_full_info')
    date_hierarchy = 'created_at'
    list_editable = ('status_badge',) if False else ()
    actions = ['mark_reviewed', 'mark_approved', 'mark_rejected', 'export_to_excel']
    change_list_template = 'admin/main/olympiadapplication/change_list.html'

    fieldsets = (
        ('Foydalanuvchi ma\'lumotlari', {
            'fields': ('user_full_info',)
        }),
        ('Ariza ma\'lumotlari', {
            'fields': ('user', 'application_type', 'olympiad', 'motivation', 'created_at', 'updated_at')
        }),
        ('Admin qarori', {
            'fields': ('status', 'admin_note')
        }),
    )

    def application_target(self, obj):
        return obj.display_title
    application_target.short_description = 'Olimpiada'

    def user_info(self, obj):
        u = obj.user
        full_name = (u.get_full_name() or u.username).strip()
        return format_html(
            '<div><strong>{}</strong><br><small style="color:#6b7280;">{}</small></div>',
            full_name, u.email or u.phone_number or '—'
        )
    user_info.short_description = 'Foydalanuvchi'

    def user_full_info(self, obj):
        if not obj.pk:
            return '—'
        u = obj.user
        html = f"""
        <div style="background:#f9fafb;padding:14px 18px;border-radius:8px;border:1px solid #e5e7eb;">
            <table style="width:100%;border-collapse:collapse;">
                <tr><td style="padding:4px 8px;color:#6b7280;width:200px;">F.I.O</td><td style="padding:4px 8px;"><strong>{u.get_full_name() or '—'}</strong></td></tr>
                <tr><td style="padding:4px 8px;color:#6b7280;">Email</td><td style="padding:4px 8px;">{u.email or '—'}</td></tr>
                <tr><td style="padding:4px 8px;color:#6b7280;">Telefon</td><td style="padding:4px 8px;">{u.phone_number or '—'}</td></tr>
                <tr><td style="padding:4px 8px;color:#6b7280;">Universitet</td><td style="padding:4px 8px;">{u.university or '—'}</td></tr>
                <tr><td style="padding:4px 8px;color:#6b7280;">Fakultet</td><td style="padding:4px 8px;">{getattr(u, 'faculty', '') or '—'}</td></tr>
                <tr><td style="padding:4px 8px;color:#6b7280;">Daraja</td><td style="padding:4px 8px;">{u.get_academic_degree_display() if u.academic_degree else '—'}</td></tr>
                <tr><td style="padding:4px 8px;color:#6b7280;">Talantli status</td><td style="padding:4px 8px;">{format_assessment_status(u)}</td></tr>
            </table>
        </div>
        """
        return mark_safe(html)
    user_full_info.short_description = 'Foydalanuvchi to\'liq ma\'lumoti'

    def status_badge(self, obj):
        colors = {
            'new': '#3b82f6',
            'reviewed': '#f59e0b',
            'approved': '#10b981',
            'rejected': '#ef4444',
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.get_status_display()
        )
    status_badge.short_description = 'Holat'

    @admin.action(description='Belgilangan arizalarni "Ko\'rib chiqildi" qilish')
    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')

    @admin.action(description='Belgilangan arizalarni "Tasdiqlash"')
    def mark_approved(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Belgilangan arizalarni "Rad etish"')
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')

    @admin.action(description='Excel formatda yuklab olish')
    def export_to_excel(self, request, queryset):
        from .admin_olympiad import generate_applications_excel
        return generate_applications_excel(queryset)
