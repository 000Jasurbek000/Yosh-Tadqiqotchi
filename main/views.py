from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm
from .models import (Olympiad, StateScholarship, BuxduScholarship, Course, ArticleBank, Announcement, User, 
                     Survey, TalentedStudentDatabase, BuxduWinnerDatabase, BuxduOlympiadWinner, BuxduOlympiad,
                     OakDatabase, Conference, DissertationBank, ResearcherRegulation, UserCourseProgress, 
                     UserModuleProgress, UserTestResult, Question, AssessmentTest, AssessmentTestResult)


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


# Olimpiadalar
class OlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiads'] = Olympiad.objects.all().order_by('-created_at')
        return context


class XalqaroOlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiads'] = Olympiad.objects.filter(type='international').order_by('-created_at')
        context['olimp_type'] = 'xalqaro'
        return context


class RespublikaOlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiads'] = Olympiad.objects.filter(type='republic').order_by('-created_at')
        context['olimp_type'] = 'respublika'
        return context


class OnlaynOlimpiadalarView(TemplateView):
    template_name = 'olimpiadalar_dynamic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['olympiads'] = Olympiad.objects.filter(type='online').order_by('-created_at')
        context['olimp_type'] = 'onlayn'
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


# Xizmatlar
class ServiceView(TemplateView):
    template_name = 'service.html'


class MaqolaJurnalTavsiyasiView(TemplateView):
    template_name = 'maqola_jurnal_tavsiyasi.html'


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
    messages.info(request, 'Tizimdan chiqdingiz.')
    return redirect('main:home')


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
    
    context = {
        'user': request.user,
        'courses_data': courses_data,
        'certificates': certificates,
        'assessment_results': assessment_results,
        'can_take_assessment': can_take_assessment,
        'assessment_wait_time': assessment_wait_time,
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
