from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import requests
from .models import (
    User, Question, Answer, Course, Module, Announcement, 
    Survey, StateScholarship, BuxduScholarship, Olympiad, 
    OakDatabase, Conference, TalentedStudentDatabase
)


def get_university_choices():
    """API dan OTMlar ro'yxatini olish"""
    try:
        response = requests.get('https://prof-emis.edu.uz/api/v2/integration/stat/public/university?limit=10000', timeout=5)
        if response.status_code == 200:
            data = response.json()
            universities = [('', 'O\'qigan/O\'qiyotgan joyingizni tanlang')]
            
            # API to'g'ridan-to'g'ri list qaytaradi
            if isinstance(data, list):
                for item in data:
                    # name_uz, name_en, name_ru kalitlaridan birini olish
                    name = item.get('name_uz') or item.get('name_en') or item.get('name_ru')
                    if name:
                        universities.append((name, name))
            
            universities.append(('Boshqa', 'Boshqa'))
            return universities
    except Exception as e:
        print(f"API dan OTM ma'lumotlarini olishda xatolik: {e}")
    
    # Agar API ishlamasa, default ro'yxat
    return [
        ('', 'O\'qigan/O\'qiyotgan joyingizni tanlang'),
        ('Toshkent davlat universiteti', 'Toshkent davlat universiteti'),
        ('O\'zbekiston Milliy universiteti', 'O\'zbekiston Milliy universiteti'),
        ('Samarqand davlat universiteti', 'Samarqand davlat universiteti'),
        ('Buxoro davlat universiteti', 'Buxoro davlat universiteti'),
        ('Boshqa', 'Boshqa'),
    ]


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


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email manzilingiz'
    }))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Ismingiz'
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Familiyangiz'
    }))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': '+998 XX XXX XX XX',
        'id': 'phone_number'
    }))
    residence_region = forms.ChoiceField(choices=REGION_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-input',
    }))
    university = forms.ChoiceField(choices=[], required=False, widget=forms.Select(attrs={
        'class': 'form-input',
    }))
    academic_degree = forms.ChoiceField(choices=DEGREE_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-input',
    }))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'residence_region', 'university', 'academic_degree', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dinamik OTM choices
        self.fields['university'].choices = get_university_choices()
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Parolni tasdiqlang'
        })


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email manzilingiz'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Parol'
    }))


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email manzilingiz'
    }))
    residence_region = forms.ChoiceField(choices=REGION_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-input',
    }))
    university = forms.ChoiceField(choices=[], required=False, widget=forms.Select(attrs={
        'class': 'form-input',
    }))
    academic_degree = forms.ChoiceField(choices=DEGREE_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-input',
    }))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-input',
        'accept': 'image/*'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'residence_region', 'university', 'academic_degree', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ismingiz'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Familiyangiz'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+998 XX XXX XX XX',
                'id': 'phone_number'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dinamik OTM choices
        self.fields['university'].choices = get_university_choices()


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
