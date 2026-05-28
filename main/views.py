from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse as reverse_url
from django.views.generic import TemplateView, View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail, EmailMessage
from django.conf import settings as django_settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json as json_module
from .chat_api import call_chat_api
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm
from .models import (Olympiad, StateScholarship, BuxduScholarship, Course, ArticleBank, Announcement, User, 
                     Survey, TalentedStudentDatabase, BuxduWinnerDatabase, BuxduOlympiadWinner, BuxduOlympiad,
                     OakDatabase, Conference, DissertationBank, ResearcherRegulation, UserCourseProgress, 
                     UserModuleProgress, UserTestResult, Question, AssessmentTest, AssessmentTestResult,
                     Literature, ScientificSupervisor, SupervisorRequest, OlympiadProgram, OlympiadApplication)
from django.utils import timezone


def index_view(request):
    announcements = Announcement.objects.order_by('-created_at')[:3]
    talented_students = User.objects.filter(status='iqtidorli').order_by('-created_at')[:4]
    context = {
        'olympiad_count': Olympiad.objects.count(),
        'scholarship_count': StateScholarship.objects.count() + BuxduScholarship.objects.count(),
        'course_count': Course.objects.count(),
        'article_count': ArticleBank.objects.count(),
        'announcements': announcements,
        'talented_students': talented_students,
    }
    return render(request, 'index.html', context)


def announcement_detail_view(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    return render(request, 'announcement_detail.html', {'announcement': announcement})


class CoursesView(LoginRequiredMixin, TemplateView):
    template_name = 'courses.html'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.filter(is_active=True).order_by('-created_at')
        return context


class CourseDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'course_detail.html'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_id, is_active=True)
        user = self.request.user
        
        # Get or create course progress
        course_progress, created = UserCourseProgress.objects.get_or_create(
            user=user,
            course=course
        )
        
        # Set started_at if first time accessing
        if created or not course_progress.started_at:
            from django.utils import timezone
            course_progress.started_at = timezone.now()
            course_progress.save()
        
        # Get all modules
        modules = course.modules.all().order_by('number')
        
        # Get user's module progress
        user_module_progress = {}
        for progress in UserModuleProgress.objects.filter(user=user, module__course=course):
            user_module_progress[progress.module.id] = progress
        
        # Determine unlock status for each module
        modules_with_status = []
        previous_completed = True
        
        for module in modules:
            progress = user_module_progress.get(module.id)
            is_completed = progress.is_completed if progress else False
            is_unlocked = previous_completed  # Unlock if previous module was completed
            
            module.is_unlocked = is_unlocked
            module.is_completed = is_completed
            module.progress = progress
            modules_with_status.append(module)
            
            previous_completed = is_completed
        
        # Check if all modules are completed
        all_completed = all(m.is_completed for m in modules_with_status)
        
        # Get certificate if exists
        from .models import Certificate
        certificate = Certificate.objects.filter(user=user, course=course).first()
        
        # Get last test result for retry timer
        from .models import UserTestResult
        from django.utils import timezone
        last_test = UserTestResult.objects.filter(user=user, course=course).order_by('-submitted_at').first()
        
        # Calculate remaining wait time (8 minutes = 480 seconds)
        can_retry = True
        wait_seconds = 0
        if last_test and not last_test.passed:
            time_since_test = (timezone.now() - last_test.submitted_at).total_seconds()
            if time_since_test < 480:  # 8 minutes
                can_retry = False
                wait_seconds = int(480 - time_since_test)
        
        context['course'] = course
        context['modules'] = modules_with_status
        context['course_progress'] = course_progress
        context['all_modules_completed'] = all_completed
        context['test_passed'] = course_progress.test_passed
        context['certificate'] = certificate
        context['last_test'] = last_test
        context['can_retry'] = can_retry
        context['wait_seconds'] = wait_seconds
        
        return context


# Module tracking and completion
@login_required
def track_presentation(request, module_id):
    from django.http import JsonResponse
    from .models import Module
    
    if request.method == 'POST':
        module = get_object_or_404(Module, pk=module_id)
        progress, created = UserModuleProgress.objects.get_or_create(
            user=request.user,
            module=module
        )
        progress.viewed_presentation = True
        progress.save()
        
        return JsonResponse({'status': 'success', 'viewed_presentation': True})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def track_video(request, module_id):
    from django.http import JsonResponse
    from .models import Module
    
    if request.method == 'POST':
        module = get_object_or_404(Module, pk=module_id)
        progress, created = UserModuleProgress.objects.get_or_create(
            user=request.user,
            module=module
        )
        progress.watched_video = True
        progress.save()
        
        return JsonResponse({'status': 'success', 'watched_video': True})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def complete_module(request, module_id):
    from django.http import JsonResponse
    from django.utils import timezone
    from .models import Module
    
    if request.method == 'POST':
        module = get_object_or_404(Module, pk=module_id)
        progress, created = UserModuleProgress.objects.get_or_create(
            user=request.user,
            module=module
        )
        
        # Mark module as completed
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
        return JsonResponse({
            'status': 'success',
            'is_completed': True,
            'message': 'Modul muvaffaqiyatli tugatildi!'
        })
    return JsonResponse({'status': 'error'}, status=400)

# Course Test Views
@login_required
def course_test_view(request, course_id):
    from .models import Module, Question, Answer
    
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    user = request.user
    
    # Check if all modules are completed
    total_modules = course.modules.count()
    completed_modules = UserModuleProgress.objects.filter(
        user=user,
        module__course=course,
        is_completed=True
    ).count()
    
    print(f"DEBUG: Total modules: {total_modules}, Completed: {completed_modules}")
    
    if completed_modules < total_modules:
        print(f"DEBUG: REDIRECT - Modules not completed")
        messages.error(request, f'Barcha modullarni tugatishingiz kerak! Tugatilgan: {completed_modules}/{total_modules}')
        return redirect('main:course_detail', pk=course_id)
    
    # Check if test already passed - allow retrying even if passed
    course_progress = UserCourseProgress.objects.filter(user=user, course=course).first()
    print(f"DEBUG: Course progress exists: {course_progress is not None}, Test passed: {course_progress.test_passed if course_progress else 'N/A'}")
    
    # Check if user needs to wait 8 minutes after failed attempt
    last_test = UserTestResult.objects.filter(user=user, course=course, passed=False).order_by('-submitted_at').first()
    if last_test:
        from django.utils import timezone
        time_since_last = timezone.now() - last_test.submitted_at
        print(f"DEBUG: Last failed test: {last_test.submitted_at}, Time since: {time_since_last.total_seconds()} seconds")
        if time_since_last.total_seconds() < 480:  # 8 minutes (changed from 600)
            wait_minutes = int((480 - time_since_last.total_seconds()) / 60) + 1
            print(f"DEBUG: REDIRECT - Need to wait {wait_minutes} minutes")
            messages.warning(request, f'Testni qayta topshirish uchun {wait_minutes} daqiqa kutishingiz kerak!')
            return redirect('main:course_detail', pk=course_id)
    
    # Allow retrying test even if passed (removed the block that prevented retrying)
    
    # Get all questions for this course
    if not course.test_set:
        print(f"DEBUG: REDIRECT - No test set assigned")
        messages.error(request, 'Ushbu kurs uchun test biriktirilmagan!')
        return redirect('main:course_detail', pk=course_id)
    
    questions = Question.objects.filter(test_set=course.test_set).prefetch_related('answers').order_by('?')[:20]  # Random 20 questions
    print(f"DEBUG: Questions count: {questions.count()}")
    
    if not questions.exists():
        print(f"DEBUG: REDIRECT - No questions available")
        messages.error(request, 'Test savollari hozircha yuklanmagan!')
        return redirect('main:course_detail', pk=course_id)
    
    print(f"DEBUG: SUCCESS - Rendering test page")
    # Calculate total time (time_per_question * total_questions)
    total_time_minutes = course.time_per_question * questions.count()
    
    context = {
        'course': course,
        'questions': questions,
        'total_time_minutes': total_time_minutes,
        'total_time_seconds': total_time_minutes * 60,
    }
    return render(request, 'course_test.html', context)

@login_required
def submit_test(request, course_id):
    from django.http import JsonResponse
    from django.utils import timezone
    from .models import Question, Answer, UserTestResult
    import json
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    user = request.user
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        # Get all questions
        questions = Question.objects.filter(test_set=course.test_set).prefetch_related('answers')
        total_questions = questions.count()
        correct_answers = 0
        
        # Check answers
        for question in questions:
            question_id = str(question.id)
            user_answer_id = answers.get(question_id)
            
            if user_answer_id:
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and str(correct_answer.id) == str(user_answer_id):
                    correct_answers += 1
        
        # Calculate percentage
        percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        passed = percentage >= course.passing_score
        
        # Save test result
        test_result = UserTestResult.objects.create(
            user=user,
            course=course,
            score=percentage,
            total_questions=total_questions,
            correct_answers=correct_answers,
            percentage=percentage,
            passed=passed
        )
        
        # Update course progress
        course_progress, created = UserCourseProgress.objects.get_or_create(
            user=user,
            course=course
        )
        course_progress.test_score = percentage
        course_progress.test_passed = passed
        
        if passed:
            course_progress.is_completed = True
            course_progress.completed_at = timezone.now()
            
            # Generate certificate automatically (only once per course)
            try:
                from main.certificate_generator import generate_certificate
                from main.models import Certificate
                from django.core.files.base import ContentFile
                
                # Check if certificate already exists for this user and course
                existing_certificate = Certificate.objects.filter(
                    user=user,
                    course=course
                ).first()
                
                if not existing_certificate:
                    # Create new certificate only if doesn't exist
                    pdf_buffer = generate_certificate(user, course, test_result)
                    certificate = Certificate.objects.create(
                        user=user,
                        course=course,
                        test_result=test_result
                    )
                    certificate.certificate_file.save(
                        f'certificate_{user.id}_{course.id}_{timezone.now().strftime("%Y%m%d")}.pdf',
                        ContentFile(pdf_buffer.getvalue())
                    )
            except Exception as cert_error:
                print(f"Certificate generation error: {cert_error}")
        
        course_progress.save()
        
        return JsonResponse({
            'success': True,
            'passed': passed,
            'percentage': percentage,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'passing_score': course.passing_score
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Iqtidorli talabalar
class IqtidorliSorovnomaView(LoginRequiredMixin, TemplateView):
    template_name = 'iqtidorli_sorovnoma.html'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['surveys'] = Survey.objects.filter(is_active=True)
        return context


class IqtidorliTestView(LoginRequiredMixin, TemplateView):
    template_name = 'iqtidorli_test.html'
    login_url = 'main:login'


class IqtidorliBazaView(LoginRequiredMixin, TemplateView):
    template_name = 'iqtidorli_baza.html'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['databases'] = TalentedStudentDatabase.objects.all()
        return context


# Stipendiyalar
class DavlatStipendiyalariView(TemplateView):
    template_name = 'davlat_stipendiyalari.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scholarships'] = StateScholarship.objects.all().order_by('-created_at')
        return context


class BuxDUStipendiyalariView(TemplateView):
    template_name = 'buxdu_stipendiyalari.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scholarships'] = BuxduScholarship.objects.all().order_by('-created_at')
        return context


class BuxDUStipendiyaBazasiView(TemplateView):
    template_name = 'buxdu_stipendiya_bazasi.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['databases'] = BuxduWinnerDatabase.objects.all().order_by('-academic_year')
        return context


def download_winner_database(request, database_id):
    """BuxDU sovrindorlar bazasi faylini yuklab berish (production media muammosini chetlab o'tadi)."""
    import mimetypes
    import os
    from django.http import FileResponse, Http404

    database = get_object_or_404(BuxduWinnerDatabase, pk=database_id)
    if not database.file:
        raise Http404('Fayl topilmadi')

    if not database.file.storage.exists(database.file.name):
        raise Http404('Fayl serverda mavjud emas')

    filename = database.file_name or os.path.basename(database.file.name)
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'

    response = FileResponse(database.file.open('rb'), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# Olimpiadalar
class OlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        # Faqat kelgusi olimpiadalarni ko'rsatish
        olympiads = Olympiad.objects.filter(date__gte=date.today()).order_by('date')
        context['olympiads'] = olympiads
        return context


class XalqaroOlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiads'] = Olympiad.objects.filter(type='international').order_by('-created_at')
        context['olimp_type'] = 'xalqaro'
        context['hero_image'] = 'assets/xalqaro_olymp.jpg'
        return context


class RespublikaOlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiads'] = Olympiad.objects.filter(type='republic').order_by('-created_at')
        context['olimp_type'] = 'respublika'
        context['hero_image'] = 'assets/olimpiada.jpg'
        return context


class OnlaynOlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiads'] = Olympiad.objects.filter(type='online').order_by('-created_at')
        context['olimp_type'] = 'onlayn'
        context['hero_image'] = 'assets/onlayn_olymp.jpg'
        return context


class BuxDUOlimpiadaGoliblarView(TemplateView):
    template_name = 'buxdu_olimpiada_goliblari.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['winners'] = BuxduOlympiadWinner.objects.all().order_by('-created_at')
        return context


class BuxDUOlimpiadalarView(TemplateView):
    template_name = 'buxdu_olimpiadalari.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        
        today = timezone.now().date()
        all_olympiads = BuxduOlympiad.objects.all()
        
        # Kutilayotgan va tugagan olimpiadalarni ajratish
        upcoming = [o for o in all_olympiads if o.date >= today]
        finished = [o for o in all_olympiads if o.date < today]
        
        # Sanaga ko'ra tartiblash
        upcoming.sort(key=lambda x: x.date)
        finished.sort(key=lambda x: x.date, reverse=True)
        
        context['upcoming_olympiads'] = upcoming
        context['finished_olympiads'] = finished
        return context


class BuxDUOlimpiadaDetailView(TemplateView):
    template_name = 'buxdu_olimpiada_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        olympiad_id = self.kwargs.get('pk')
        olympiad = get_object_or_404(BuxduOlympiad, pk=olympiad_id)
        context['olympiad'] = olympiad
        context['gallery_images'] = olympiad.images.all()
        return context


# Ilmiy nashrlar
class MahalliyOAKJurnallariView(TemplateView):
    template_name = 'oak_jurnallari_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['journals'] = OakDatabase.objects.filter(type='local').order_by('-created_at')
        context['oak_type'] = 'mahalliy'
        return context


class XalqaroOAKJurnallariView(TemplateView):
    template_name = 'oak_jurnallari_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['journals'] = OakDatabase.objects.filter(type='international').order_by('-created_at')
        context['oak_type'] = 'xalqaro'
        return context


class XalqaroKonferensiyalarView(TemplateView):
    template_name = 'konferensiyalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conferences'] = Conference.objects.filter(type='international').order_by('-created_at')
        context['konf_type'] = 'xalqaro'
        return context


class RespublikaKonferensiyalarView(TemplateView):
    template_name = 'konferensiyalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conferences'] = Conference.objects.filter(type='republic').order_by('-created_at')
        context['konf_type'] = 'respublika'
        return context


class DissertatsiyalarBankiView(TemplateView):
    template_name = 'dissertatsiyalar_banki.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dissertations'] = DissertationBank.objects.all().order_by('-created_at')
        return context


class MaqolalarBankiView(TemplateView):
    template_name = 'maqolalar_banki.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = ArticleBank.objects.all().order_by('-created_at')
        return context


class PlatformaHaqidaView(TemplateView):
    template_name = 'platforma_haqida.html'


class IqtidorYoliView(LoginRequiredMixin, TemplateView):
    template_name = 'iqtidor_yoli.html'
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Iqtidor Yo'li sahifasiga kirish uchun login qiling.")
            return redirect('main:login')

        # Faqat iqtidorli talabalar kira oladi (adminlar bundan mustasno)
        is_admin = request.user.is_staff or request.user.is_superuser
        if not is_admin and request.user.assessment_status != 'iqtidorli':
            messages.warning(
                request,
                "Iqtidor Yo'li sahifasi faqat iqtidorli talabalar uchun. "
                "Avval saralash testidan o'tib iqtidorli holatga ega bo'ling."
            )
            return redirect('main:assessment_test')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['volunteer_application'] = OlympiadApplication.objects.filter(
            user=self.request.user,
            application_type='volunteer',
        ).order_by('-created_at').first()
        return context


class IlmiyRahbarlarView(TemplateView):
    template_name = 'ilmiy_rahbarlar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supervisors = list(ScientificSupervisor.objects.filter(is_active=True))

        user_status = {}
        accepted_supervisor = None
        if self.request.user.is_authenticated:
            user_requests = SupervisorRequest.objects.filter(
                student=self.request.user
            ).select_related('supervisor')
            for r in user_requests:
                existing = user_status.get(r.supervisor_id)
                if existing is None or (existing == 'rejected' and r.status != 'rejected'):
                    user_status[r.supervisor_id] = r.status
                if r.status == 'accepted':
                    accepted_supervisor = r.supervisor

        context['supervisors'] = supervisors
        context['user_status'] = user_status
        context['accepted_supervisor'] = accepted_supervisor
        return context


@login_required(login_url='/login/')
def send_supervisor_request(request, supervisor_id):
    if request.method != 'POST':
        return redirect('main:ilmiy_rahbarlar')

    supervisor = get_object_or_404(ScientificSupervisor, pk=supervisor_id, is_active=True)
    user = request.user

    if not supervisor.email:
        messages.error(request, f"{supervisor.full_name} email manzili kiritilmagan. Murojaat yuborib bo'lmaydi.")
        return redirect('main:ilmiy_rahbarlar')

    # Talabaning allaqachon ilmiy rahbari bor-yo'qligini tekshirish
    existing_accepted = SupervisorRequest.objects.filter(
        student=user, status='accepted'
    ).select_related('supervisor').first()
    if existing_accepted:
        messages.error(
            request,
            f"Sizda allaqachon ilmiy rahbar bor: {existing_accepted.supervisor.full_name}. "
            f"Rahbarni o'zgartirish uchun admin bilan bog'laning."
        )
        return redirect('main:ilmiy_rahbarlar')

    # Sig'im tekshiruvi
    if supervisor.is_full:
        messages.error(
            request,
            f"{supervisor.full_name} hozircha to'liq band ({supervisor.max_students} ta talaba). Murojaat yuborib bo'lmaydi."
        )
        return redirect('main:ilmiy_rahbarlar')

    # Allaqachon mavjud so'rov tekshiruvi (shu rahbarga)
    existing = SupervisorRequest.objects.filter(
        student=user, supervisor=supervisor, status='pending'
    ).first()
    if existing:
        messages.warning(request, f"{supervisor.full_name}ga avval yuborilgan murojaat hali javob kutmoqda.")
        return redirect('main:ilmiy_rahbarlar')

    # Yangi so'rov yaratish
    sup_request = SupervisorRequest.objects.create(student=user, supervisor=supervisor)

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
    degree = user.get_academic_degree_display() if user.academic_degree else '—'

    # Accept / Reject havolalari
    base_url = request.build_absolute_uri('/').rstrip('/')
    accept_url = base_url + reverse_url('main:supervisor_decision', args=[sup_request.token, 'accept'])
    reject_url = base_url + reverse_url('main:supervisor_decision', args=[sup_request.token, 'reject'])

    subject = f"Rahbarlik so'rovi — {full_name}"

    # HTML email
    html_body = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"></head>
    <body style="font-family:Arial,sans-serif;background:#f5f3ff;margin:0;padding:30px 0;">
      <div style="max-width:620px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.08);">
        <div style="background:linear-gradient(135deg,#8b5cf6,#d946ef);color:#fff;padding:28px 32px;">
          <h1 style="margin:0;font-size:22px;">🎓 Yangi rahbarlik so'rovi</h1>
          <p style="margin:6px 0 0;opacity:0.92;font-size:14px;">Yosh Tadqiqotchi platformasi</p>
        </div>

        <div style="padding:28px 32px;">
          <p style="font-size:15px;color:#1f1b2d;margin:0 0 16px;">
            Assalomu alaykum, hurmatli <b>{supervisor.full_name}</b>!
          </p>
          <p style="font-size:14px;color:#4b4b5a;line-height:1.6;margin:0 0 22px;">
            Sizga Yosh Tadqiqotchi platformasi orqali yangi rahbarlik so'rovi keldi.
            Quyida talabaning ma'lumotlari ko'rsatilgan. Iltimos, murojaatni
            <b>qabul qiling</b> yoki <b>rad eting</b>.
          </p>

          <table style="width:100%;border-collapse:collapse;background:#f9fafb;border-radius:10px;overflow:hidden;font-size:14px;color:#1f1b2d;">
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;width:35%;color:#6b7280;">F.I.O</td><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;font-weight:600;">{full_name}</td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;">Email</td><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;"><a href="mailto:{user.email}" style="color:#8b5cf6;text-decoration:none;">{user.email or '—'}</a></td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;">Telefon</td><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;">{user.phone_number or '—'}</td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;">Universitet</td><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;">{user.university or '—'}</td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;">Fakultet</td><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;">{user.faculty or '—'}</td></tr>
            <tr><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;">Ilmiy daraja</td><td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;">{degree}</td></tr>
            <tr><td style="padding:10px 14px;color:#6b7280;">Yashash xududi</td><td style="padding:10px 14px;">{user.residence_region or '—'}</td></tr>
          </table>

          <div style="background:#f5f3ff;border-left:4px solid #8b5cf6;padding:14px 18px;border-radius:8px;margin:22px 0;font-size:13.5px;color:#4b4b5a;line-height:1.65;">
            <b>Murojaat mazmuni:</b><br>
            Men, {full_name}, sizning ilmiy-pedagogik tajribangiz va mutaxassisligingiz bilan tanishib chiqdim.
            Sizdan iltimos qilaman — meni o'z rahbarligingizga qabul qilishingiz va ilmiy tadqiqot
            faoliyatim bo'yicha yo'naltirishingizni so'rayman.
          </div>

          <p style="font-size:14px;color:#4b4b5a;margin:24px 0 14px;text-align:center;">
            Iltimos, quyidagi tugmalardan birini bosing:
          </p>

          <table style="width:100%;margin:0 auto;">
            <tr>
              <td style="padding:6px;text-align:center;">
                <a href="{accept_url}" style="display:inline-block;background:linear-gradient(135deg,#10b981,#059669);color:#fff;padding:13px 32px;border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;box-shadow:0 8px 20px rgba(16,185,129,0.3);">
                  ✓ Qabul qilish
                </a>
              </td>
              <td style="padding:6px;text-align:center;">
                <a href="{reject_url}" style="display:inline-block;background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;padding:13px 32px;border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;box-shadow:0 8px 20px rgba(239,68,68,0.3);">
                  ✗ Rad etish
                </a>
              </td>
            </tr>
          </table>

          <p style="font-size:12px;color:#9ca3af;margin:24px 0 0;text-align:center;line-height:1.5;">
            Bu xat avtomatik tarzda Yosh Tadqiqotchi platformasidan yuborildi.<br>
            Talaba bilan to'g'ridan-to'g'ri bog'lanish uchun bu xatga javob yozing.
          </p>
        </div>
      </div>
    </body></html>
    """

    # Oddiy text variant
    text_body = (
        f"Assalomu alaykum, hurmatli {supervisor.full_name}!\n\n"
        f"Sizga yangi rahbarlik so'rovi keldi.\n\n"
        f"Talaba: {full_name}\n"
        f"Email: {user.email or '—'}\n"
        f"Telefon: {user.phone_number or '—'}\n"
        f"Universitet: {user.university or '—'}\n"
        f"Fakultet: {user.faculty or '—'}\n\n"
        f"Qabul qilish: {accept_url}\n"
        f"Rad etish: {reject_url}\n"
    )

    try:
        email_msg = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[supervisor.email],
            reply_to=[user.email] if user.email else None,
        )
        email_msg.content_subtype = 'html'
        email_msg.send(fail_silently=False)
        messages.success(
            request,
            f"Murojaatingiz {supervisor.full_name}ga muvaffaqiyatli yuborildi. "
            f"Javob kelguncha kuting. Profilingizda holatini kuzatishingiz mumkin."
        )
    except Exception as e:
        sup_request.delete()
        messages.error(request, f"Xatolik yuz berdi: {e}")

    return redirect('main:ilmiy_rahbarlar')


def supervisor_decision(request, token, action):
    """Email orqali kelgan link bilan rahbar so'rovni qabul/rad qiladi."""
    sup_request = get_object_or_404(SupervisorRequest, token=token)
    supervisor = sup_request.supervisor
    student = sup_request.student

    # Allaqachon javob berilgan bo'lsa
    if sup_request.status != 'pending':
        return render(request, 'supervisor_decision.html', {
            'request_obj': sup_request,
            'supervisor': supervisor,
            'student': student,
            'already_decided': True,
        })

    if action not in ('accept', 'reject'):
        return render(request, 'supervisor_decision.html', {
            'invalid': True,
        })

    # POST — yakuniy qaror
    if request.method == 'POST':
        full_name = f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username

        if action == 'accept':
            # Sig'im qayta tekshirish
            if supervisor.is_full:
                return render(request, 'supervisor_decision.html', {
                    'request_obj': sup_request,
                    'supervisor': supervisor,
                    'student': student,
                    'full_error': True,
                })

            # Talabada allaqachon rahbar bor-yo'qligini tekshirish
            already_has = SupervisorRequest.objects.filter(
                student=student, status='accepted'
            ).select_related('supervisor').first()
            if already_has:
                return render(request, 'supervisor_decision.html', {
                    'request_obj': sup_request,
                    'supervisor': supervisor,
                    'student': student,
                    'student_has_supervisor': True,
                    'current_supervisor': already_has.supervisor,
                })

            sup_request.status = 'accepted'
            sup_request.decided_at = timezone.now()
            sup_request.save()

            # Talabaning boshqa kutilayotgan so'rovlarini avtomatik rad etish
            SupervisorRequest.objects.filter(
                student=student, status='pending'
            ).exclude(pk=sup_request.pk).update(
                status='rejected',
                decided_at=timezone.now(),
                decision_reason='Talaba boshqa rahbar bilan ishlay boshladi (avtomatik)'
            )

            # Talabaga xabar yuborish
            try:
                accept_email_body = (
                    f"Assalomu alaykum, {full_name}!\n\n"
                    f"Xush xabar — {supervisor.full_name} sizning rahbarlik so'rovingizni "
                    f"qabul qildi.\n\n"
                    f"Rahbar bilan bog'lanish:\n"
                    f"  Email: {supervisor.email or '—'}\n"
                    f"  Telefon: {supervisor.phone or '—'}\n\n"
                    f"Iloji bo'lsa, rahbar bilan bog'lanib, keyingi qadamlarni muhokama qiling.\n\n"
                    f"Hurmat bilan,\n"
                    f"Yosh Tadqiqotchi platformasi"
                )
                send_mail(
                    subject=f"Rahbarlik so'rovingiz qabul qilindi — {supervisor.full_name}",
                    message=accept_email_body,
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email] if student.email else [],
                    fail_silently=True,
                )
            except Exception:
                pass

        else:  # reject
            sup_request.status = 'rejected'
            sup_request.decided_at = timezone.now()
            sup_request.save()

            try:
                reject_email_body = (
                    f"Assalomu alaykum, {full_name}.\n\n"
                    f"Afsuski, {supervisor.full_name} sizning rahbarlik so'rovingizni "
                    f"qabul qila olmadi.\n\n"
                    f"Boshqa ilmiy rahbarga murojaat qilib ko'rishingiz mumkin.\n\n"
                    f"Hurmat bilan,\n"
                    f"Yosh Tadqiqotchi platformasi"
                )
                send_mail(
                    subject=f"Rahbarlik so'rovi haqida — {supervisor.full_name}",
                    message=reject_email_body,
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email] if student.email else [],
                    fail_silently=True,
                )
            except Exception:
                pass

        return render(request, 'supervisor_decision.html', {
            'request_obj': sup_request,
            'supervisor': supervisor,
            'student': student,
            'done': True,
            'action': action,
        })

    # GET — tasdiqlash sahifasi
    return render(request, 'supervisor_decision.html', {
        'request_obj': sup_request,
        'supervisor': supervisor,
        'student': student,
        'action': action,
        'confirm_needed': True,
    })


class AdabiyotlarView(TemplateView):
    template_name = 'adabiyotlar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        field_filter = self.request.GET.get('field', '')
        search = self.request.GET.get('q', '').strip()
        qs = Literature.objects.all()
        if field_filter:
            qs = qs.filter(field=field_filter)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(author__icontains=search)
        context['books'] = qs
        context['field_choices'] = Literature.FIELD_CHOICES
        context['active_field'] = field_filter
        context['search_query'] = search
        return context


# Xizmatlar
class ServiceView(LoginRequiredMixin, View):
    template_name = 'service.html'
    login_url = '/login/'

    def get(self, request):
        user = request.user
        context = {
            'prefill_name': f"{user.last_name} {user.first_name}",
            'prefill_email': user.email or '',
            'prefill_phone': user.phone_number or '',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        notes = request.POST.get('notes', '').strip()
        service_type = request.POST.get('serviceType', 'edit')
        publisher = request.POST.get('publisher', '')
        article_type = request.POST.get('article_type', '')
        tariff = request.POST.get('tariff', '')
        total_price = request.POST.get('total_price', '')
        extras = request.POST.getlist('extras')

        service_label = 'Tarjima' if service_type == 'translate' else 'Tahrirlash'
        extras_text = '\n   '.join(f'• {e}' for e in extras) if extras else 'Yo\'q'

        subject = f"Maqola tahriri/tarjima so'rovi — {full_name}"
        body = f"""Yangi buyurtma keldi!

👤 Foydalanuvchi: {user.get_full_name()} ({user.email})
🏫 Universitet  : {user.university or 'Ko\'rsatilmagan'}
🎓 Fakultet     : {user.faculty or 'Ko\'rsatilmagan'}

━━━ BUYURTMA MA'LUMOTLARI ━━━
Xizmat turi          : {service_label}
Nashriyot / standart : {publisher}
Maqola turi          : {article_type}
Tarif                : {tariff}
Qo'shimcha opsiyalar : {extras_text}
Jami narx            : {total_price} UZS

━━━ MUROJAAT MA'LUMOTLARI ━━━
F.I.O   : {full_name}
Email   : {email}
Izoh    : {notes or 'Yo\'q'}
"""
        try:
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                to=[django_settings.ADMIN_EMAIL],
            )
            uploaded_file = request.FILES.get('article_file')
            if uploaded_file:
                msg.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
            msg.send(fail_silently=False)
            messages.success(request, 'Buyurtmangiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog\'lanamiz.')
        except Exception:
            messages.error(request, 'Xabar yuborishda xatolik yuz berdi. Qayta urinib ko\'ring.')

        context = {
            'prefill_name': full_name,
            'prefill_email': email,
            'prefill_phone': user.phone_number or '',
        }
        return render(request, self.template_name, context)


class MaqolaJurnalTavsiyasiView(LoginRequiredMixin, View):
    template_name = 'maqola_jurnal_tavsiyasi.html'
    login_url = '/login/'

    def get(self, request):
        user = request.user
        context = {
            'prefill_name': f"{user.last_name} {user.first_name}",
            'prefill_email': user.email or '',
            'prefill_phone': user.phone_number or '',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        article_topic = request.POST.get('article_topic', '').strip()

        subject = f"Maqolaga mos jurnal tavsiyasi so'rovi — {full_name}"
        body = f"""Yangi jurnal tavsiyasi so'rovi keldi!

📌 Xizmat turi: Maqola mazmuniga mos jurnalni tavsiya etish

👤 Foydalanuvchi: {user.get_full_name()} ({user.email})
🏫 Universitet  : {user.university or 'Ko\'rsatilmagan'}
🎓 Fakultet     : {user.faculty or 'Ko\'rsatilmagan'}

━━━ MUROJAAT MA'LUMOTLARI ━━━
F.I.O          : {full_name}
Email          : {email}
Telefon        : {phone or 'Ko\'rsatilmagan'}
Maqola mavzusi : {article_topic or 'Ko\'rsatilmagan'}
"""
        try:
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                to=[django_settings.ADMIN_EMAIL],
            )
            uploaded_file = request.FILES.get('article_file')
            if uploaded_file:
                msg.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
            msg.send(fail_silently=False)
            messages.success(request, 'So\'rovingiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog\'lanamiz.')
        except Exception:
            messages.error(request, 'Xabar yuborishda xatolik yuz berdi. Qayta urinib ko\'ring.')

        context = {
            'prefill_name': full_name,
            'prefill_email': email,
            'prefill_phone': phone,
        }
        return render(request, self.template_name, context)


class IlmiyNizomlarView(TemplateView):
    template_name = 'ilmiy_nizomlar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regulations'] = ResearcherRegulation.objects.all().order_by('-created_at')
        return context


# Auth
def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Username ni email dan yaratamiz
            email = form.cleaned_data.get('email')
            user = form.save(commit=False)
            user.username = email.split('@')[0] + str(User.objects.count() + 1)
            user.save()
            messages.success(request, f'{user.first_name}, siz muvaffaqiyatli ro\'yxatdan o\'tdingiz!')
            # Backend ni aniqlash (EmailBackend ishlatamiz)
            login(request, user, backend='main.backends.EmailBackend')
            return redirect('main:home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Form field nomi username lekin email kiritiladi
            password = form.cleaned_data.get('password')
            # Email orqali authenticate qilamiz (custom backend ishlatadi)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Xush kelibsiz, {user.first_name or user.email}!')
                next_url = request.GET.get('next', 'main:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Email yoki parol noto\'g\'ri!')
        else:
            messages.error(request, 'Email yoki parol noto\'g\'ri. Iltimos, qaytadan urinib ko\'ring.')
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Tizimdan muvaffaqiyatli chiqdingiz.')
    return redirect('main:login')


@login_required
def profile_view(request):
    # Get user's course progress
    user_courses = UserCourseProgress.objects.filter(
        user=request.user
    ).select_related('course').order_by('-started_at')
    
    # Calculate progress for each course
    courses_data = []
    for progress in user_courses:
        course = progress.course
        total_modules = course.modules.count()
        completed_modules = UserModuleProgress.objects.filter(
            user=request.user,
            module__course=course,
            is_completed=True
        ).count()
        
        progress_percentage = 0
        if total_modules > 0:
            progress_percentage = int((completed_modules / total_modules) * 100)
        
        courses_data.append({
            'progress': progress,
            'course': course,
            'total_modules': total_modules,
            'completed_modules': completed_modules,
            'progress_percentage': progress_percentage,
        })
    
    # Get user's certificates
    from main.models import Certificate
    certificates = Certificate.objects.filter(
        user=request.user
    ).select_related('course', 'test_result').order_by('-issued_at')
    
    # Get assessment test results
    assessment_results = AssessmentTestResult.objects.filter(
        user=request.user
    ).select_related('assessment_test').order_by('-submitted_at')
    
    # Check if can take assessment test
    can_take_assessment = True
    assessment_wait_time = None
    if request.user.assessment_next_attempt:
        from django.utils import timezone
        now = timezone.now()
        if now < request.user.assessment_next_attempt:
            can_take_assessment = False
            wait_seconds = int((request.user.assessment_next_attempt - now).total_seconds())
            assessment_wait_time = {
                'seconds': wait_seconds,
                'hours': wait_seconds // 3600,
                'minutes': (wait_seconds % 3600) // 60
            }
    
    # Ilmiy rahbarlik so'rovlari
    supervisor_requests = SupervisorRequest.objects.filter(
        student=request.user
    ).select_related('supervisor').order_by('-created_at')
    accepted_supervisors = [r.supervisor for r in supervisor_requests if r.status == 'accepted']

    # Olimpiada va volontyor arizalari
    olympiad_applications = OlympiadApplication.objects.filter(
        user=request.user
    ).select_related('olympiad').order_by('-created_at')

    context = {
        'user': request.user,
        'courses_data': courses_data,
        'certificates': certificates,
        'assessment_results': assessment_results,
        'can_take_assessment': can_take_assessment,
        'assessment_wait_time': assessment_wait_time,
        'supervisor_requests': supervisor_requests,
        'accepted_supervisors': accepted_supervisors,
        'olympiad_applications': olympiad_applications,
    }
    return render(request, 'profile.html', context)


@login_required
def download_certificate(request, certificate_id):
    """Download certificate as PDF with FIO filename"""
    from django.http import FileResponse, Http404
    from .models import Certificate
    
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    if not certificate.certificate_file:
        raise Http404("Certificate file not found")
    
    # Create filename with user's FIO (Full Name)
    user = request.user
    fio = f"{user.last_name}_{user.first_name}".replace(' ', '_')
    filename = f"Sertifikat_{fio}.pdf"
    
    response = FileResponse(certificate.certificate_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def settings_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profilingiz muvaffaqiyatli yangilandi!')
                return redirect('main:settings')
        
        elif form_type == 'password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Parolingiz muvaffaqiyatli o\'zgartirildi!')
                return redirect('main:settings')
            else:
                messages.error(request, 'Parolni o\'zgartirishda xatolik yuz berdi.')
    
    user_form = UserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    
    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'settings.html', context)


# ==================== SARALASH TESTI (ASSESSMENT TEST) ====================

@login_required(login_url='main:login')
def assessment_test_view(request):
    """Saralash testi haqida ma'lumot sahifasi"""
    assessment_test = AssessmentTest.objects.filter(is_active=True).first()
    
    # Test mavjud bo'lmasa ham sahifani ko'rsatamiz
    user = request.user
    can_attempt = True
    wait_time = None
    last_result = None
    
    if assessment_test:
        # Foydalanuvchi allaqachon test topshirganmi?
        if user.assessment_next_attempt:
            from django.utils import timezone
            now = timezone.now()
            
            if now < user.assessment_next_attempt:
                can_attempt = False
                wait_seconds = int((user.assessment_next_attempt - now).total_seconds())
                wait_time = {
                    'seconds': wait_seconds,
                    'hours': wait_seconds // 3600,
                    'minutes': (wait_seconds % 3600) // 60
                }
        
        # Oxirgi natijani olish
        last_result = AssessmentTestResult.objects.filter(
            user=user,
            assessment_test=assessment_test
        ).order_by('-submitted_at').first()
    
    context = {
        'assessment_test': assessment_test,
        'can_attempt': can_attempt,
        'wait_time': wait_time,
        'last_result': last_result,
        'user_status': user.assessment_status,
    }
    
    return render(request, 'assessment_test.html', context)


@login_required(login_url='main:login')
def start_assessment_test(request):
    """Saralash testini boshlash"""
    assessment_test = AssessmentTest.objects.filter(is_active=True).first()
    
    if not assessment_test:
        messages.error(request, 'Test mavjud emas.')
        return redirect('main:assessment_test')
    
    # Test to'plami borligini tekshirish
    if not assessment_test.test_set:
        messages.error(request, 'Test savollari mavjud emas.')
        return redirect('main:assessment_test')
    
    # Savollarni olish
    questions = Question.objects.filter(test_set=assessment_test.test_set).prefetch_related('answers').order_by('number')
    
    if not questions.exists():
        messages.error(request, 'Test savollari topilmadi.')
        return redirect('main:assessment_test')
    
    # Foydalanuvchi qayta urinish qila olishini tekshirish
    user = request.user
    if user.assessment_next_attempt:
        from django.utils import timezone
        now = timezone.now()
        
        if now < user.assessment_next_attempt:
            messages.warning(request, 'Siz hali testni qayta topshira olmaysiz. Iltimos, kutish vaqti tugashini kuting.')
            return redirect('main:assessment_test')
    
    context = {
        'assessment_test': assessment_test,
        'questions': questions,
        'total_questions': questions.count(),
        'time_limit_seconds': assessment_test.time_limit * 60,  # Daqiqalarni soniyalarga
    }
    
    return render(request, 'assessment_test_questions.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta

@login_required(login_url='main:login')
@require_http_methods(["POST"])
def submit_assessment_test(request):
    """Saralash testi natijalarini saqlash"""
    import json
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        
        assessment_test = AssessmentTest.objects.filter(is_active=True).first()
        
        if not assessment_test or not assessment_test.test_set:
            return JsonResponse({'success': False, 'error': 'Test topilmadi'}, status=404)
        
        # Savollar va javoblarni olish
        questions = Question.objects.filter(test_set=assessment_test.test_set).prefetch_related('answers')
        total_questions = questions.count()
        correct_answers = 0
        
        # Javoblarni tekshirish
        for question in questions:
            question_id = str(question.id)
            user_answer_id = answers.get(question_id)
            
            if user_answer_id:
                # Foydalanuvchi javob bergan
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and str(correct_answer.id) == str(user_answer_id):
                    correct_answers += 1
            # Agar javob bermagan bo'lsa, xato deb hisoblanadi (correct_answers o'zgarmaydi)
        
        # Foizni hisoblash
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        passed = percentage >= assessment_test.pass_percentage
        
        # Natijani saqlash
        result = AssessmentTestResult.objects.create(
            user=request.user,
            assessment_test=assessment_test,
            score=correct_answers,
            total_questions=total_questions,
            correct_answers=correct_answers,
            percentage=percentage,
            passed=passed,
            time_taken=time_taken
        )
        
        # Foydalanuvchi ma'lumotlarini yangilash
        user = request.user
        user.assessment_score = percentage
        user.assessment_taken_at = timezone.now()
        
        # Keyingi urinish vaqtini belgilash (1 soatdan keyin)
        user.assessment_next_attempt = timezone.now() + timedelta(hours=assessment_test.retry_delay_hours)
        
        # Agar o'tgan bo'lsa, statusni o'zgartirish
        if passed:
            user.assessment_status = 'iqtidorli'
            user.status = 'iqtidorli'  # Umumiy statusni ham o'zgartirish
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'passed': passed,
            'percentage': round(percentage, 2),
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'new_status': user.assessment_status
        })
        
    except Exception as e:
        print(f"Assessment test submission error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def chat_view(request):
    try:
        data = json_module.loads(request.body)
        user_message = data.get('message', '').strip()
        history = data.get('history', [])
        if not user_message:
            return JsonResponse({'reply': 'Xabar bo\'sh bo\'lmasligi kerak.'})

        system_prompt = """
Siz "Tadqiqotchi AI" nomli ilmiy-tadqiqot yordamchisisiz.

O'ZINGIZ HAQIDA:
- Ismingiz: Tadqiqotchi AI
- Siz ilmiy tadqiqot, ta'lim va akademik mavzularda yordam beradigan AI yordamchisiz.
- "ChatGPT", "OpenAI" yoki boshqa kompaniya nomini tilga olmang.

SUHBAT QOIDALARI:
- Suhbat tarixini eslab qoling. Foydalanuvchining oldingi savollariga va sizning oldingi javoblaringizga asoslanib javob bering.
- Masalan, agar foydalanuvchi "magistrlik nima" deb so'ragan, keyin "uni qanday olaman" desa — magistrlik darajasini qanday olish haqida javob bering, o'zingiz haqingizda emas.

JAVOB BERISH QOIDALARI:
1. Javob 500 belgidan oshmasin — qisqa, aniq va tushunarli yozing.
2. Hech qachon havola, manba, URL yoki "Batafsil..." kabi qo'shimcha qo'shmang.
3. Markdown formatdan foydalaning: muhim so'zlar uchun **bold** ishlatsangiz mumkin.
4. Agar ma'lumot topilmasa, "Kechirasiz, bu mavzu bo'yicha aniq ma'lumot topa olmadim." deb ayting.
5. O'zbek tilida javob bering. Foydalanuvchi boshqa tilda yozsa — shu tilda javob bering.
"""

        # Suhbat tarixini API formatiga keltirish (oxirgi 10 ta xabar)
        messages_list = []
        for h in history[-10:]:
            role = h.get('role')
            content = h.get('content', '').strip()
            if role in ('user', 'assistant') and content:
                messages_list.append({"role": role, "content": content})
        messages_list.append({"role": "user", "content": user_message})

        reply, error = call_chat_api(messages_list, system_prompt)
        if error:
            return JsonResponse({'reply': error})
        return JsonResponse({'reply': reply})

    except json_module.JSONDecodeError:
        return JsonResponse({'reply': 'Noto\'g\'ri so\'rov formati.'})
    except Exception as e:
        print(f"Chat error: {e}")
        return JsonResponse({'reply': 'Xatolik yuz berdi. Qayta urinib ko\'ring.'})


# ──────────────────────────── Olimpiada dasturi ────────────────────────────
class OlympiadProgramDetailView(LoginRequiredMixin, View):
    """Iqtidor Yo'li sahifasidan olimpiada kartochkasi bosilganda
    ushbu olimpiadaga oid topshiriqlar bazasi va ariza yuborish sahifasi."""
    login_url = 'main:login'
    template_name = 'olympiad_program.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        # Faqat iqtidorli yoki admin ko'ra oladi
        if not (request.user.is_staff or request.user.assessment_status == 'iqtidorli'):
            messages.warning(request, "Bu sahifaga faqat saralash testidan o'tgan iqtidorli talabalar kira oladi.")
            return redirect('main:iqtidor_yoli')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, code):
        # OlympiadProgram.OLYMPIAD_CHOICES dagi mavjud kodlardan ekanligini tekshiramiz
        valid_codes = [c[0] for c in OlympiadProgram.OLYMPIAD_CHOICES]
        if code not in valid_codes:
            messages.error(request, "Bunday olimpiada topilmadi.")
            return redirect('main:iqtidor_yoli')

        program = OlympiadProgram.objects.filter(code=code, is_active=True).first()
        if not program:
            # Admin hali bu olimpiada uchun ma'lumotlarni kiritmagan
            display_title = dict(OlympiadProgram.OLYMPIAD_CHOICES).get(code, 'Olimpiada')
            return render(request, 'olympiad_program_not_ready.html', {
                'olympiad_title': display_title,
                'olympiad_code': code,
            })

        existing_application = OlympiadApplication.objects.filter(
            user=request.user, olympiad=program, application_type='olympiad'
        ).order_by('-created_at').first()
        context = {
            'program': program,
            'existing_application': existing_application,
        }
        return render(request, self.template_name, context)


def _send_application_admin_email(user, application, target_title, email_heading):
    """Olimpiada/volontyor arizasi haqida adminga email yuborish."""
    try:
        u = user
        full_name = u.get_full_name() or u.username
        motivation = application.motivation or ''
        subject = f"{email_heading} — {target_title}"
        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto;background:#f9fafb;padding:24px;">
            <div style="background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <h2 style="color:#4f46e5;margin:0 0 8px;">{email_heading}</h2>
                <p style="color:#6b7280;margin:0 0 18px;">Yosh Tadqiqotchi platformasi orqali yangi ariza yuborildi.</p>

                <div style="background:#eef2ff;padding:14px 18px;border-radius:8px;margin-bottom:18px;">
                    <strong style="color:#4338ca;">Olimpiada:</strong> {target_title}
                </div>

                <h3 style="color:#1f2937;margin:0 0 10px;">Foydalanuvchi ma'lumotlari</h3>
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:6px 0;color:#6b7280;width:160px;">F.I.O</td><td style="padding:6px 0;"><strong>{full_name}</strong></td></tr>
                    <tr><td style="padding:6px 0;color:#6b7280;">Email</td><td style="padding:6px 0;">{u.email or '—'}</td></tr>
                    <tr><td style="padding:6px 0;color:#6b7280;">Telefon</td><td style="padding:6px 0;">{u.phone_number or '—'}</td></tr>
                    <tr><td style="padding:6px 0;color:#6b7280;">Universitet</td><td style="padding:6px 0;">{u.university or '—'}</td></tr>
                    <tr><td style="padding:6px 0;color:#6b7280;">Fakultet</td><td style="padding:6px 0;">{getattr(u, 'faculty', '') or '—'}</td></tr>
                    <tr><td style="padding:6px 0;color:#6b7280;">Daraja</td><td style="padding:6px 0;">{u.get_academic_degree_display() if u.academic_degree else '—'}</td></tr>
                </table>

                <h3 style="color:#1f2937;margin:18px 0 10px;">Motivatsiya</h3>
                <div style="background:#f3f4f6;padding:14px 18px;border-radius:8px;color:#1f2937;white-space:pre-wrap;">
                    {motivation or 'Foydalanuvchi qo\'shimcha matn yozmagan.'}
                </div>

                <p style="margin:24px 0 0;color:#6b7280;font-size:13px;">
                    Arizani admin panelda ko'rish: Admin → Olimpiada arizalari → #{application.id}
                </p>
            </div>
        </div>
        """
        msg = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[django_settings.DEFAULT_FROM_EMAIL],
            reply_to=[u.email] if u.email else None,
        )
        msg.content_subtype = 'html'
        msg.send(fail_silently=True)
    except Exception as e:
        print(f"Application email error: {e}")


@login_required(login_url='main:login')
@require_POST
def submit_olympiad_application(request, code):
    """Ariza yuborish — DB ga yozadi va adminga email yuboradi."""
    program = get_object_or_404(OlympiadProgram, code=code, is_active=True)

    if not (request.user.is_staff or request.user.assessment_status == 'iqtidorli'):
        messages.error(request, "Faqat iqtidorli talabalar ariza topshira oladi.")
        return redirect('main:iqtidor_yoli')

    # Takroriy arizani oldini olish (yangi yoki ko'rib chiqilayotgan ariza bo'lsa)
    duplicate = OlympiadApplication.objects.filter(
        user=request.user,
        olympiad=program,
        application_type='olympiad',
        status__in=['new', 'reviewed']
    ).first()
    if duplicate:
        messages.warning(request,
            f"Siz allaqachon ushbu olimpiadaga ariza yuborgansiz. Holati: «{duplicate.get_status_display()}». "
            "Admin ko'rib chiqishini kuting.")
        return redirect('main:olympiad_program', code=code)

    motivation = (request.POST.get('motivation') or '').strip()

    application = OlympiadApplication.objects.create(
        user=request.user,
        application_type='olympiad',
        olympiad=program,
        motivation=motivation or None,
    )

    _send_application_admin_email(
        request.user, application, program.title, '🏆 Yangi olimpiada arizasi'
    )

    messages.success(request,
        f"✅ Arizangiz muvaffaqiyatli yuborildi! «{program.title}» olimpiadasi uchun "
        "admin tomonidan ko'rib chiqilgach javob beriladi.")
    return redirect('main:olympiad_program', code=code)


@login_required(login_url='main:login')
@require_POST
def submit_volunteer_application(request):
    """Volontyor jamoasiga ariza — sahifasiz, to'g'ridan-to'g'ri yuboriladi."""
    if not (request.user.is_staff or request.user.assessment_status == 'iqtidorli'):
        messages.error(request, "Faqat iqtidorli talabalar ariza topshira oladi.")
        return redirect('main:iqtidor_yoli')

    duplicate = OlympiadApplication.objects.filter(
        user=request.user,
        application_type='volunteer',
        status__in=['new', 'reviewed'],
    ).first()
    if duplicate:
        messages.warning(request,
            f"Siz allaqachon volontyor jamoasiga ariza yuborgansiz. "
            f"Holati: «{duplicate.get_status_display()}». Admin ko'rib chiqishini kuting.")
        return redirect('main:iqtidor_yoli')

    motivation = (request.POST.get('motivation') or '').strip()
    target_title = OlympiadApplication.VOLUNTEER_TITLE

    application = OlympiadApplication.objects.create(
        user=request.user,
        application_type='volunteer',
        olympiad=None,
        motivation=motivation or None,
    )

    _send_application_admin_email(
        request.user, application, target_title, '🤝 Yangi volontyor arizasi'
    )

    messages.success(request,
        "✅ Volontyor jamoasiga arizangiz muvaffaqiyatli yuborildi! "
        "Admin tomonidan ko'rib chiqilgach javob beriladi.")
    return redirect('main:iqtidor_yoli')
