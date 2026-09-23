import os
import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    User, Question, Answer, Course, Module, Announcement, 
    Survey, StateScholarship, BuxduScholarship, Olympiad, 
    OakDatabase, Conference, TalentedStudentDatabase
)


def get_university_choices():
    """universities.json faylidan OTMlar ro'yxatini olish"""
    try:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'xalikova_project', 'universities.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        universities = [('', 'O\'qigan/O\'qiyotgan joyingizni tanlang')]
        for item in data:
            name = item.get('name')
            if name:
                universities.append((name, name))
        universities.append(('Boshqa', 'Boshqa'))
        return universities
    except Exception as e:
        print(f"universities.json dan ma'lumotlarini olishda xatolik: {e}")
    
    # Agar fayl o'qilmasa, default ro'yxat
    return [
        ('', 'O\'qigan/O\'qiyotgan joyingizni tanlang'),
        ('Toshkent davlat universiteti', 'Toshkent davlat universiteti'),
        ('O\'zbekiston Milliy universiteti', 'O\'zbekiston Milliy universiteti'),
        ('Samarqand davlat universiteti', 'Samarqand davlat universiteti'),
        ('Buxoro davlat universiteti', 'Buxoro davlat universiteti'),
        ('Boshqa', 'Boshqa'),
    ]


BUXDU_FACULTIES = [
    'Aniq fanlar va intellektual muhandislik texnologiyalari ilmiy-tadqiqot instituti',
    'Tabiiy fanlar va agroinnovatsiyalar ilmiy-tadqiqot instituti',
    'Yuridik fakulteti',
    'Filologiya fakulteti',
    'Tarix fakulteti',
    'Xorijiy tillar',
    "Sport va san'at fakulteti",
    'Davlat auditi fakulteti',
    'Iqtisodiyot va turizm fakulteti',
]

FACULTY_CHOICES = [('', 'Fakultetni tanlang')] + [(f, f) for f in BUXDU_FACULTIES]

REGION_CHOICES = [
    ('', 'Yashash xududingizni tanlang'),
    ('Toshkent shahri', 'Toshkent shahri'),
    ('Andijon', 'Andijon'),
    ('Buxoro', 'Buxoro'),
    ('Jizzax', 'Jizzax'),
    ('Qashqadaryo', 'Qashqadaryo'),
    ('Navoiy', 'Navoiy'),
    ('Namangan', 'Namangan'),
    ('Samarqand', 'Samarqand'),
    ('Surxondaryo', 'Surxondaryo'),
    ('Sirdaryo', 'Sirdaryo'),
    ('Farg\'ona', 'Farg\'ona'),
    ('Xorazm', 'Xorazm'),
    ('Qoraqalpog\'iston', 'Qoraqalpog\'iston Respublikasi'),
]

DEGREE_CHOICES = [
    ('', 'Darajangizni tanlang'),
    ('bakalavr', 'Bakalavr'),
    ('magistr', 'Magistr'),
    ('phd', 'PhD (Falsafa doktori)'),
    ('dsc', 'DSc (Fan doktori)'),
]

COURSE_STAGE_CHOICES = [
    ('', 'Kursni tanlang'),
    ('1-kurs', '1-kurs'),
    ('2-kurs', '2-kurs'),
    ('3-kurs', '3-kurs'),
    ('4-kurs', '4-kurs'),
]


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Ismingiz',
        'required': True,
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Familiyangiz',
        'required': True,
    }))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': '+998 XX XXX XX XX',
        'id': 'phone_number',
        'required': True,
    }))
    residence_region = forms.ChoiceField(choices=REGION_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'required': True,
    }))
    university = forms.ChoiceField(choices=[], required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'id': 'id_university',
        'required': True,
    }))
    faculty = forms.ChoiceField(choices=FACULTY_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'id': 'id_faculty',
        'required': True,
    }))
    education_direction = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': "Ta'lim yo'nalishi",
        'required': True,
    }))
    education_stage = forms.ChoiceField(choices=COURSE_STAGE_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'required': True,
    }))
    academic_degree = forms.ChoiceField(choices=DEGREE_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'required': True,
    }))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'required': True,
    }))

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'residence_region',
            'university', 'faculty', 'education_direction', 'education_stage',
            'academic_degree', 'role', 'password1', 'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.fields.pop('email', None)
        from .i18n import t
        self.fields['university'].choices = get_university_choices()
        self.fields['faculty'].choices = [('', t('form.select_faculty'))] + [(f, f) for f in BUXDU_FACULTIES]
        self.fields['education_stage'].choices = [('', t('form.select_course'))] + [
            (key, t(f'stage.{key}')) for key, _label in COURSE_STAGE_CHOICES if key
        ]
        self.fields['academic_degree'].choices = [('', t('form.select_degree'))] + [
            (key, t(f'degree.{key}')) for key, _label in DEGREE_CHOICES if key
        ]
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Parol',
            'required': True,
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Parolni tasdiqlang',
            'required': True,
        })
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['password1'].widget.attrs.pop('aria-describedby', None)
        self.fields['password2'].widget.attrs.pop('aria-describedby', None)

    def clean_first_name(self):
        value = (self.cleaned_data.get('first_name') or '').strip()
        if not value:
            raise forms.ValidationError('Ism majburiy.')
        return value

    def clean_last_name(self):
        value = (self.cleaned_data.get('last_name') or '').strip()
        if not value:
            raise forms.ValidationError('Familiya majburiy.')
        return value

    def clean_phone_number(self):
        from .phone_utils import normalize_phone, phone_digits
        raw = self.cleaned_data.get('phone_number') or ''
        compact = normalize_phone(raw)
        digits = phone_digits(compact)
        if len(digits) != 9:
            raise forms.ValidationError('Telefon raqamini to\'liq kiriting: +998 XX XXX XX XX')
        qs = User.objects.filter(phone_number=compact)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Bu telefon raqam allaqachon ro\'yxatdan o\'tgan.')
        return compact

    def clean(self):
        cleaned_data = super().clean()
        university = cleaned_data.get('university')
        faculty = cleaned_data.get('faculty')
        residence_region = cleaned_data.get('residence_region')
        academic_degree = cleaned_data.get('academic_degree')

        if not residence_region:
            self.add_error('residence_region', 'Yashash xududi majburiy.')

        if not university:
            self.add_error('university', 'O\'qigan/O\'qiyotgan joyni tanlash majburiy.')

        if not faculty or not str(faculty).strip():
            self.add_error('faculty', 'Fakultetni tanlang.')

        if not (cleaned_data.get('education_direction') or '').strip():
            self.add_error('education_direction', "Ta'lim yo'nalishini kiriting.")

        if not (cleaned_data.get('education_stage') or '').strip():
            self.add_error('education_stage', "Ta'lim bosqichi / kursni kiriting.")

        if not academic_degree:
            self.add_error('academic_degree', 'Ilmiy darajani tanlang.')

        if not cleaned_data.get('role'):
            self.add_error('role', 'Rolni tanlang.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.faculty = (self.cleaned_data.get('faculty') or '').strip()
        user.education_direction = (self.cleaned_data.get('education_direction') or '').strip()
        user.education_stage = (self.cleaned_data.get('education_stage') or '').strip()
        user.email = None
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': '+998 XX XXX XX XX',
        'id': 'phone_number',
        'autocomplete': 'tel',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Parol'
    }))

    error_messages = {
        'invalid_login': 'Telefon raqam yoki parol noto\'g\'ri.',
        'inactive': 'Bu akkaunt faol emas.',
    }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email (ixtiyoriy)'
    }))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Ismingiz',
        'required': True,
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Familiyangiz',
        'required': True,
    }))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': '+998 XX XXX XX XX',
        'id': 'phone_number',
        'required': True,
    }))
    residence_region = forms.ChoiceField(choices=REGION_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'required': True,
    }))
    university = forms.ChoiceField(choices=[], required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'id': 'id_university',
        'required': True,
    }))
    faculty = forms.ChoiceField(choices=FACULTY_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'id': 'id_faculty',
        'required': True,
    }))
    education_direction = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': "Ta'lim yo'nalishi",
        'required': True,
    }))
    education_stage = forms.ChoiceField(choices=COURSE_STAGE_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'required': True,
    }))
    academic_degree = forms.ChoiceField(choices=DEGREE_CHOICES, required=True, widget=forms.Select(attrs={
        'class': 'form-input',
        'required': True,
    }))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-input',
        'accept': 'image/*'
    }))

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'residence_region',
            'university', 'faculty', 'education_direction', 'education_stage',
            'academic_degree', 'profile_image',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .i18n import t
        self.fields['university'].choices = get_university_choices()
        stage_choices = [('', t('form.select_course'))] + [
            (key, t(f'stage.{key}')) for key, _label in COURSE_STAGE_CHOICES if key
        ]
        current = (getattr(self.instance, 'education_stage', '') or '').strip()
        if current and current not in dict(stage_choices):
            stage_choices.append((current, current))
        self.fields['education_stage'].choices = stage_choices
        self.fields['academic_degree'].choices = [('', t('form.select_degree'))] + [
            (key, t(f'degree.{key}')) for key, _label in DEGREE_CHOICES if key
        ]
        faculty_choices = [('', t('form.select_faculty'))] + [(f, f) for f in BUXDU_FACULTIES]
        current_faculty = (getattr(self.instance, 'faculty', '') or '').strip()
        if current_faculty and current_faculty not in dict(faculty_choices):
            faculty_choices.append((current_faculty, current_faculty))
        self.fields['faculty'].choices = faculty_choices

    def clean_first_name(self):
        value = (self.cleaned_data.get('first_name') or '').strip()
        if not value:
            raise forms.ValidationError('Ism majburiy.')
        return value

    def clean_last_name(self):
        value = (self.cleaned_data.get('last_name') or '').strip()
        if not value:
            raise forms.ValidationError('Familiya majburiy.')
        return value

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            return None
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Bu email allaqachon band.')
        return email

    def clean_phone_number(self):
        from .phone_utils import normalize_phone, phone_digits
        raw = self.cleaned_data.get('phone_number') or ''
        compact = normalize_phone(raw)
        digits = phone_digits(compact)
        if len(digits) != 9:
            raise forms.ValidationError('Telefon raqamini to\'liq kiriting.')
        qs = User.objects.filter(phone_number=compact)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Bu telefon raqam allaqachon band.')
        return compact

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('residence_region'):
            self.add_error('residence_region', 'Yashash xududi majburiy.')
        if not cleaned_data.get('university'):
            self.add_error('university', 'O\'qigan/O\'qiyotgan joyni tanlash majburiy.')
        if not (cleaned_data.get('faculty') or '').strip():
            self.add_error('faculty', 'Fakultetni tanlang.')
        if not (cleaned_data.get('education_direction') or '').strip():
            self.add_error('education_direction', "Ta'lim yo'nalishini kiriting.")
        if not (cleaned_data.get('education_stage') or '').strip():
            self.add_error('education_stage', "Ta'lim bosqichi / kursni kiriting.")
        if not cleaned_data.get('academic_degree'):
            self.add_error('academic_degree', 'Ilmiy darajani tanlang.')
        return cleaned_data


# Question with Answers Form
class QuestionWithAnswersForm(forms.ModelForm):
    answer_a = forms.CharField(max_length=500, label='A) variant', required=True, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px;',
        'placeholder': 'A variantini kiriting'
    }))
    answer_b = forms.CharField(max_length=500, label='B) variant', required=True, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px;',
        'placeholder': 'B variantini kiriting'
    }))
    answer_c = forms.CharField(max_length=500, label='C) variant', required=True, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px;',
        'placeholder': 'C variantini kiriting'
    }))
    answer_d = forms.CharField(max_length=500, label='D) variant', required=True, widget=forms.TextInput(attrs={
        'style': 'width: 100%; padding: 8px;',
        'placeholder': 'D variantini kiriting'
    }))
    correct_answer = forms.ChoiceField(
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        label='To\'g\'ri javob',
        widget=forms.RadioSelect,
        required=True
    )
    
    class Meta:
        model = Question
        fields = ['test_set', 'number', 'text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'style': 'width: 100%;',
                'placeholder': 'Savol matnini kiriting'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Load existing answers
            answers = list(self.instance.answers.all().order_by('id'))
            if len(answers) >= 4:
                self.fields['answer_a'].initial = answers[0].text
                self.fields['answer_b'].initial = answers[1].text
                self.fields['answer_c'].initial = answers[2].text
                self.fields['answer_d'].initial = answers[3].text
                
                # Find correct answer
                for idx, ans in enumerate(answers[:4]):
                    if ans.is_correct:
                        self.fields['correct_answer'].initial = chr(65 + idx)  # A, B, C, D
    
    def save(self, commit=True):
        """Save the question instance. Answers are handled by admin.save_model()"""
        instance = super().save(commit=commit)
        return instance


# Admin Form for Course
class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Masalan: Python dasturlash asoslari',
                'style': 'width: 100%;'
            }),
            'short_description': forms.Textarea(attrs={
                'placeholder': 'Kurs haqida qisqacha ma\'lumot yozing (3-5 jumla)',
                'rows': 3,
                'style': 'width: 100%;'
            }),
        }


# Admin Form for Module
class ModuleAdminForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Masalan: Kirish, O\'zgaruvchilar',
                'style': 'width: 100%;'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Modul haqida qisqa ma\'lumot',
                'rows': 3,
                'style': 'width: 100%;'
            }),
            'youtube_url': forms.URLInput(attrs={
                'placeholder': 'https://youtube.com/watch?v=...',
                'style': 'width: 100%;'
            }),
        }


# Admin Form for Announcement
class AnnouncementAdminForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'
        widgets = {
            'author': forms.TextInput(attrs={
                'placeholder': 'Masalan: X.U.Mirovna',
                'style': 'width: 100%;'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'E\'lon sarlavhasi',
                'style': 'width: 100%;'
            }),
            'short_text': forms.Textarea(attrs={
                'placeholder': 'E\'lonning qisqacha matni (2-3 qator)',
                'rows': 2,
                'style': 'width: 100%;'
            }),
            'detailed_text': forms.Textarea(attrs={
                'placeholder': 'E\'lonning to\'liq matni',
                'rows': 5,
                'style': 'width: 100%;'
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg',
                'style': 'width: 100%;'
            }),
        }


# Admin Form for Survey
class SurveyAdminForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Masalan: Talabalar fikri so\'rovnomasi',
                'style': 'width: 100%;'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'So\'rovnoma haqida qisqa ma\'lumot',
                'rows': 3,
                'style': 'width: 100%;'
            }),
            'link': forms.URLInput(attrs={
                'placeholder': 'https://forms.google.com/...',
                'style': 'width: 100%;'
            }),
        }


# Admin Form for Olympiad
class OlympiadAdminForm(forms.ModelForm):
    class Meta:
        model = Olympiad
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Masalan: Xalqaro Matematika Olimpiadasi',
                'style': 'width: 100%;'
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Masalan: Matematika, Fizika',
                'style': 'width: 100%;'
            }),
            'country': forms.TextInput(attrs={
                'placeholder': 'Masalan: O\'zbekiston, AQSh',
                'style': 'width: 100%;'
            }),
            'short_description': forms.Textarea(attrs={
                'placeholder': 'Olimpiada haqida qisqa ma\'lumot',
                'rows': 3,
                'style': 'width: 100%;'
            }),
            'registration_link': forms.URLInput(attrs={
                'placeholder': 'https://olimpiada.uz/register',
                'style': 'width: 100%;'
            }),
        }
