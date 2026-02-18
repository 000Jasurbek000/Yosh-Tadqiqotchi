from django.db import models
from django.contrib.auth.models import AbstractUser


# 1. Foydalanuvchi (Custom User)
class User(AbstractUser):
    DEGREE_CHOICES = [
        ('', 'Tanlanmagan'),
        ('bakalavr', 'Bakalavr'),
        ('magistr', 'Magistr'),
        ('phd', 'PhD (Falsafa doktori)'),
        ('dsc', 'DSc (Fan doktori)'),
    ]
    
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon raqam')
    residence_region = models.CharField(max_length=100, blank=True, null=True, verbose_name='Yashash xudud')
    university = models.CharField(max_length=200, blank=True, null=True, verbose_name='O\'qigan/O\'qiyotgan joy')
    academic_degree = models.CharField(max_length=20, choices=DEGREE_CHOICES, blank=True, default='', verbose_name='Ilmiy daraja')
    status = models.CharField(max_length=50, default='talaba', verbose_name='Status')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='Profil rasmi')
    
    # Saralash testi (Assessment Test) ma'lumotlari
    assessment_score = models.FloatField(default=0, verbose_name='Saralash testi natijasi (%)')
    assessment_status = models.CharField(max_length=20, default='oddiy', verbose_name='Talaba holati')  # 'oddiy' yoki 'iqtidorli'
    assessment_taken_at = models.DateTimeField(null=True, blank=True, verbose_name='Saralash testi topshirilgan vaqt')
    assessment_next_attempt = models.DateTimeField(null=True, blank=True, verbose_name='Keyingi urinish vaqti')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.email


# 2. E'lonlar
class Announcement(models.Model):
    author = models.CharField(max_length=255, verbose_name='Muallif', help_text='E\'lon muallifining ismi (masalan: X.U.Mirovna)')
    title = models.CharField(max_length=255, verbose_name='Sarlavha', help_text='E\'lon sarlavhasini kiriting')
    short_text = models.TextField(verbose_name='Qisqa matn', help_text='E\'lonning qisqacha matni (2-3 qator)')
    date = models.DateField(verbose_name='Sana', help_text='E\'lon sanasini tanlang')
    detailed_text = models.TextField(verbose_name='Batafsil matn', help_text='E\'lonning to\'liq matni')
    image = models.ImageField(upload_to='announcements/', blank=True, null=True, verbose_name='Rasm (fayl)', help_text='E\'lon uchun rasm yuklang (JPG, PNG)')
    image_url = models.URLField(blank=True, null=True, verbose_name='Rasm URL', help_text='Yoki rasm URL manzilini kiriting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'announcements'
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"
        ordering = ['-date']

    def __str__(self):
        return self.title
    
    def get_image_url(self):
        """Rasm URL yoki yuklangan rasm manzilini qaytaradi"""
        if self.image:
            return self.image.url
        return self.image_url


# 4. So'rovnomalar
class Survey(models.Model):
    title = models.CharField(max_length=255, verbose_name='Sarlavha', default='So\'rovnoma', help_text='So\'rovnoma sarlavhasini kiriting')
    description = models.TextField(verbose_name='Tavsif', blank=True, default='', help_text='So\'rovnoma haqida qisqa ma\'lumot')
    link = models.URLField(verbose_name='Havola', default='https://forms.google.com', help_text='Google Forms yoki boshqa so\'rovnoma havolasi')
    is_active = models.BooleanField(default=True, verbose_name='Faol', help_text='So\'rovnoma faolmi? (belgilangan bo\'lsa, saytda ko\'rsatiladi)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'surveys'
        verbose_name = 'So\'rovnoma'
        verbose_name_plural = 'So\'rovnomalar'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# 5. Iqtidorli talabalar bazasi
class TalentedStudentDatabase(models.Model):
    academic_year = models.CharField(max_length=50, verbose_name='O\'quv yili', help_text='O\'quv yilini kiriting (masalan: 2023-2024)')
    file_name = models.CharField(max_length=255, verbose_name='Fayl nomi', default='Iqtidorli talabalar ro\'yxati', help_text='Fayl nomi (masalan: Iqtidorli talabalar 2023-2024)')
    file_format = models.CharField(max_length=10, default='PDF', verbose_name='Format', help_text='Fayl formati (PDF, DOCX, XLSX)')
    file = models.FileField(upload_to='talented_students/', verbose_name='Fayl', help_text='Iqtidorli talabalar ro\'yxatini yuklang (PDF, DOCX, XLSX)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'talented_students_database'
        verbose_name = 'Iqtidorli talabalar bazasi'
        verbose_name_plural = 'Iqtidorli talabalar bazasi'
        ordering = ['-academic_year']

    def __str__(self):
        return f"{self.academic_year} - {self.file_name}"


# 6. Davlat stipendiyalari
class StateScholarship(models.Model):
    name = models.CharField(max_length=255, verbose_name='Stipendiya nomi', help_text='Stipendiya nomini kiriting (masalan: Prezident stipendiyasi)')
    short_description = models.TextField(verbose_name='Qisqacha tavsif', help_text='Stipendiya haqida qisqa ma\'lumot (kimlar uchun, qancha miqdor)')
    regulation_link = models.URLField(verbose_name='Nizom havolasi', help_text='Stipendiya nizomiga havola (https://...)')
    application_link = models.URLField(verbose_name='Ariza topshirish havolasi', help_text='Ariza topshirish uchun havola (https://...)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'state_scholarships'
        verbose_name = 'Davlat stipendiyasi'
        verbose_name_plural = 'Davlat stipendiyalari'

    def __str__(self):
        return self.name


# 7. BuxDU stipendiyalari
class BuxduScholarship(models.Model):
    name = models.CharField(max_length=255, verbose_name='Stipendiya nomi', help_text='BuxDU stipendiya nomini kiriting')
    short_description = models.TextField(verbose_name='Qisqacha tavsif', help_text='Stipendiya shartlari va talablari haqida ma\'lumot')
    regulation_file = models.FileField(upload_to='scholarships/regulations/', verbose_name='Nizom fayli', help_text='Stipendiya nizomini yuklang (PDF, DOCX)')
    application_link = models.URLField(verbose_name='Ariza topshirish havolasi', help_text='Onlayn ariza topshirish uchun havola')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'buxdu_scholarships'
        verbose_name = 'BuxDU stipendiyasi'
        verbose_name_plural = 'BuxDU stipendiyalari'

    def __str__(self):
        return self.name


# 8. BuxDU sovrindorlar bazasi
class BuxduWinnerDatabase(models.Model):
    academic_year = models.CharField(max_length=20, verbose_name='O\'quv yili', help_text='Masalan: 2023-2024')
    scholarship_type = models.CharField(max_length=255, verbose_name='Stipendiya turi', help_text='Stipendiya turini kiriting (masalan: BuxDU rektori stipendiyasi)')
    file_name = models.CharField(max_length=255, verbose_name='Fayl nomi', help_text='G\'oliblar ro\'yxati fayl nomi')
    file = models.FileField(upload_to='buxdu_winners/', verbose_name='Fayl', help_text='G\'oliblar ro\'yxatini yuklang (PDF, XLSX)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'buxdu_winner_database'
        verbose_name = 'BuxDU sovrindorlar bazasi'
        verbose_name_plural = 'BuxDU sovrindorlar bazalari'
        ordering = ['-academic_year']

    def __str__(self):
        return f"{self.scholarship_type} ({self.academic_year})"


# 9. Turli olimpiadalar
class Olympiad(models.Model):
    TYPE_CHOICES = [
        ('international', 'Xalqaro'),
        ('republic', 'Respublika'),
        ('online', 'Onlayn'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='international', verbose_name='Olimpiada turi', help_text='Olimpiada turini tanlang')
    subject = models.CharField(max_length=255, verbose_name='Fan', help_text='Olimpiada fani (masalan: Matematika, Fizika)')
    name = models.CharField(max_length=255, verbose_name='Olimpiada nomi', help_text='Olimpiadaning to\'liq nomi')
    country = models.CharField(max_length=100, verbose_name='Davlat', help_text='Olimpiada o\'tkaziladigan davlat (masalan: O\'zbekiston, AQSh)')
    short_description = models.TextField(verbose_name='Qisqacha tavsif', help_text='Olimpiada haqida qisqa ma\'lumot')
    information_letter = models.FileField(upload_to='olympiads/info_letters/', blank=True, null=True, verbose_name='Ma\'lumot xati', help_text='Olimpiada haqida rasmiy ma\'lumot xati (PDF)')
    registration_link = models.URLField(verbose_name='Ro\'yxatdan o\'tish havolasi', help_text='Olimpiadaga ro\'yxatdan o\'tish uchun havola')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'olympiads'
        verbose_name = 'Olimpiada'
        verbose_name_plural = 'Olimpiadalar'

    def __str__(self):
        return f"{self.name} ({self.subject})"


# 10. BuxDU olimpiada g'oliblari
class BuxduOlympiadWinner(models.Model):
    olympiad_name = models.CharField(max_length=255, verbose_name='Olimpiada nomi', help_text='Olimpiada nomini kiriting')
    subject = models.CharField(max_length=255, verbose_name='Fan', help_text='Olimpiada fani (masalan: Matematika)')
    academic_year = models.CharField(max_length=20, verbose_name='O\'quv yili', help_text='Masalan: 2023-2024')
    file_name = models.CharField(max_length=255, verbose_name='Fayl nomi', help_text='G\'oliblar ro\'yxati fayl nomi')
    file = models.FileField(upload_to='buxdu_olympiad_winners/', verbose_name='Fayl', help_text='G\'oliblar ro\'yxatini yuklang (PDF, XLSX)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'buxdu_olympiad_winners'
        verbose_name = "BuxDU olimpiada g'olibi"
        verbose_name_plural = "BuxDU olimpiada g'oliblari"
        ordering = ['-academic_year']

    def __str__(self):
        return f"{self.olympiad_name} - {self.subject} ({self.academic_year})"


# 11. BuxDU olimpiadalari
class BuxduOlympiad(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Kutilmoqda'),
        ('finished', 'Tugagan'),
    ]
    
    image = models.ImageField(upload_to='buxdu_olympiads/images/', verbose_name='Rasm', help_text='Olimpiada uchun rasm yuklang (JPG, PNG)')
    subject = models.CharField(max_length=255, verbose_name='Fan', help_text='Olimpiada fani (masalan: Fizika)')
    date = models.DateField(verbose_name='Sana', help_text='Olimpiada o\'tkaziladigan sana')
    description = models.TextField(verbose_name='Tavsif', help_text='Olimpiada haqida batafsil ma\'lumot')
    program_file = models.FileField(upload_to='buxdu_olympiads/programs/', verbose_name='Dastur fayli', help_text='Olimpiada dasturini yuklang (PDF)')
    registration_link_1 = models.URLField(verbose_name='Ro\'yxatdan o\'tish 1', help_text='Birinchi ro\'yxatdan o\'tish havolasi')
    registration_link_2 = models.URLField(blank=True, null=True, verbose_name='Ro\'yxatdan o\'tish 2', help_text='Ikkinchi ro\'yxatdan o\'tish havolasi (ixtiyoriy)')
    
    # Tugagan olimpiadalar uchun foto galereya
    result_file = models.FileField(
        upload_to='buxdu_olympiads/results/', 
        blank=True, 
        null=True, 
        verbose_name='Natija fayli', 
        help_text='Tugagan olimpiada natijasi (PDF, DOCX, XLSX)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'buxdu_olympiads'
        verbose_name = 'BuxDU olimpiadasi'
        verbose_name_plural = 'BuxDU olimpiadalari'
        ordering = ['-date']

    @property
    def status(self):
        """Olimpiada statusini sanaga qarab avtomatik aniqlash"""
        if not self.date:
            return 'upcoming'
        
        from django.utils import timezone
        
        today = timezone.now().date()
        if self.date < today:
            return 'finished'
        return 'upcoming'
    
    @property
    def status_display(self):
        """Status nomini ko'rsatish"""
        return 'Tugagan' if self.status == 'finished' else 'Kutilmoqda'
    
    @property
    def is_finished(self):
        """Olimpiada tugaganmi?"""
        return self.status == 'finished'
    
    @property
    def gallery_images(self):
        """Barcha galereya rasmlarini olish"""
        return self.images.all()

    def __str__(self):
        return f"{self.subject} - {self.date}"


# BuxDU olimpiadasi foto galereya modeli
class BuxduOlympiadImage(models.Model):
    olympiad = models.ForeignKey(
        BuxduOlympiad, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Olimpiada'
    )
    image = models.ImageField(
        upload_to='buxdu_olympiads/gallery/', 
        verbose_name='Rasm',
        help_text='Olimpiada jarayonidan foto'
    )
    caption = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name='Tavsif',
        help_text='Rasm tavsifi (ixtiyoriy)'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Yuklangan vaqt')
    
    class Meta:
        db_table = 'buxdu_olympiad_images'
        verbose_name = 'Olimpiada rasmi'
        verbose_name_plural = 'Olimpiada rasmlari'
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"{self.olympiad.subject} - Rasm #{self.id}"


# 12. OAK bazasi
class OakDatabase(models.Model):
    TYPE_CHOICES = [
        ('local', 'Mahalliy'),
        ('international', 'Xalqaro'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Turi', help_text='Jurnal turini tanlang (Mahalliy yoki Xalqaro)')
    journal_name = models.CharField(max_length=255, verbose_name='Jurnal nomi', help_text='OAK jurnali nomini kiriting')
    fields = models.TextField(verbose_name='Yo\'nalishlar', help_text='Jurnal qabul qiladigan yo\'nalishlar (vergul bilan ajratib yozing)')
    database_link = models.URLField(verbose_name='Baza havolasi', help_text='Jurnal bazasiga havola (https://...)')
    editorial_link = models.URLField(verbose_name='Tahririyat havolasi', help_text='Tahririyat sahifasiga havola')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'oak_database'
        verbose_name = 'OAK bazasi'
        verbose_name_plural = 'OAK bazalari'

    def __str__(self):
        return f"{self.journal_name} ({self.get_type_display()})"


# 13. Konferensiyalar
class Conference(models.Model):
    TYPE_CHOICES = [
        ('republic', 'Respublika'),
        ('international', 'Xalqaro'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Turi', help_text='Konferensiya turini tanlang')
    name = models.CharField(max_length=255, verbose_name='Nomi', help_text='Konferensiya nomini kiriting')
    information_letter = models.FileField(upload_to='conferences/info_letters/', verbose_name='Ma\'lumot xati', help_text='Konferensiya haqida ma\'lumot xati (PDF)')
    organizer_link = models.URLField(verbose_name='Tashkilotchi havolasi', help_text='Tashkilotchi tashkilot sahifasiga havola')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conferences'
        verbose_name = 'Konferensiya'
        verbose_name_plural = 'Konferensiyalar'

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


# 14. Dissertatsiyalar banki
class DissertationBank(models.Model):
    database_type = models.CharField(max_length=255, verbose_name='Baza turi', help_text='Dissertatsiya bazasi turi (masalan: DSc, PhD)')
    direction = models.CharField(max_length=255, verbose_name='Yo\'nalish', help_text='Ilmiy yo\'nalish (masalan: Pedagogika, Iqtisodiyot)')
    link = models.URLField(verbose_name='Havola', help_text='Dissertatsiya bazasiga havola')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dissertation_bank'
        verbose_name = 'Dissertatsiya banki'
        verbose_name_plural = 'Dissertatsiyalar banki'

    def __str__(self):
        return f"{self.database_type} - {self.direction}"


# 15. Maqolalar banki
class ArticleBank(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nomi', help_text='Maqola bazasi nomini kiriting')
    short_guide = models.TextField(verbose_name='Qisqa qo\'llanma', help_text='Bazadan foydalanish bo\'yicha qisqa qo\'llanma')
    database_link = models.URLField(verbose_name='Baza havolasi', help_text='Maqolalar bazasiga havola')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'article_bank'
        verbose_name = 'Maqola banki'
        verbose_name_plural = 'Maqolalar banki'

    def __str__(self):
        return self.name


# 16. Tadqiqotchilar nizomi
class ResearcherRegulation(models.Model):
    regulation_name = models.CharField(max_length=255, verbose_name='Nizom nomi', help_text='Nizom nomini kiriting')
    file = models.FileField(upload_to='regulations/', verbose_name='Fayl', help_text='Nizom faylini yuklang (PDF, DOCX)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'researcher_regulations'
        verbose_name = 'Tadqiqotchi nizomi'
        verbose_name_plural = 'Tadqiqotchilar nizomlari'

    def __str__(self):
        return self.regulation_name


# 17. Kurslar
class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name='Kurs nomi', help_text='Kursning to\'liq nomini kiriting (masalan: Python dasturlash asoslari)')
    short_description = models.TextField(default='', verbose_name='Qisqacha tavsif', help_text='Kurs haqida qisqacha ma\'lumot (3-5 jumla)')
    image = models.ImageField(upload_to='courses/', blank=True, null=True, verbose_name='Kurs rasmi', help_text='Kurs uchun rasm yuklang (PNG, JPG)')
    module_count = models.IntegerField(default=1, verbose_name='Modullar soni', help_text='Kursda nechta modul bo\'lishini kiriting (masalan: 5)')
    test_set = models.ForeignKey('TestSet', on_delete=models.SET_NULL, blank=True, null=True, related_name='courses', verbose_name='Test to\'plami', help_text='Kurs uchun tayyor test to\'plamini tanlang')
    test_file = models.FileField(upload_to='courses/tests/', blank=True, null=True, verbose_name='Test fayli (DOCX)', help_text='DOCX formatdagi test faylini yuklang (ixtiyoriy)')
    time_per_question = models.IntegerField(default=2, verbose_name='Har bir savol uchun vaqt (daqiqa)', help_text='Har bir savol uchun berilgan vaqt (daqiqalarda, masalan: 2)')
    passing_score = models.IntegerField(default=70, verbose_name='O\'tish bali (%)', help_text='Testni o\'tish uchun minimal ball (%, masalan: 70)')
    is_active = models.BooleanField(default=True, verbose_name='Faol', help_text='Kurs faolmi? (belgilangan bo\'lsa, foydalanuvchilar ko\'radi)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        verbose_name = 'Kurs'
        verbose_name_plural = 'Kurslar'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# 18. Kurs modullar
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name='Kurs', help_text='Modulni tegishli kursga bog\'lash')
    number = models.IntegerField(verbose_name='Modul raqami', help_text='Modul tartib raqami (1, 2, 3...)')
    name = models.CharField(max_length=255, verbose_name='Modul nomi', help_text='Modul nomini kiriting (masalan: Kirish, Asosiy tushunchalar)')
    description = models.TextField(verbose_name='Qisqacha ma\'lumot', help_text='Modul haqida qisqa ma\'lumot yozing')
    presentation = models.FileField(upload_to='modules/presentations/', blank=True, null=True, verbose_name='Taqdimot', help_text='PowerPoint yoki PDF taqdimot fayli')
    youtube_url = models.URLField(blank=True, null=True, verbose_name='YouTube video URL', help_text='YouTube video havolasini joylashtiring (masalan: https://youtube.com/watch?v=...)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'modules'
        verbose_name = 'Modul'
        verbose_name_plural = 'Modullar'
        ordering = ['course', 'number']
        unique_together = ['course', 'number']

    def __str__(self):
        return f"{self.course.name} - Modul {self.number}: {self.name}"


# 18. Test to'plami (alohida test nomi bilan)
class TestSet(models.Model):
    name = models.CharField(max_length=200, verbose_name='Test nomi', help_text='Test to\'plami nomini kiriting (masalan: Python asoslari testi)')
    description = models.TextField(blank=True, null=True, verbose_name='Tavsif', help_text='Test to\'plami haqida qisqa ma\'lumot')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test_sets'
        verbose_name = 'Test to\'plami'
        verbose_name_plural = 'Test to\'plamlari'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# 19. Test savollari
class Question(models.Model):
    test_set = models.ForeignKey(TestSet, on_delete=models.CASCADE, related_name='questions', verbose_name='Test to\'plami', null=True, blank=True, help_text='Savolni tegishli test to\'plamiga biriktiring')
    number = models.IntegerField(verbose_name='Savol raqami', help_text='Savol tartib raqami (1, 2, 3...)')
    text = models.TextField(verbose_name='Savol matni', help_text='Savolning to\'liq matnini kiriting')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questions'
        verbose_name = 'Savol'
        verbose_name_plural = 'Savollar'
        ordering = ['test_set', 'number']
        unique_together = ['test_set', 'number']

    def __str__(self):
        if self.test_set:
            return f"{self.test_set.name} - Savol {self.number}"
        return f"Savol {self.number}"


# 20. Javob variantlari
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Savol', help_text='Javobni tegishli savolga biriktiring')
    text = models.CharField(max_length=500, verbose_name='Javob matni', help_text='Javob variantini kiriting')
    is_correct = models.BooleanField(default=False, verbose_name='To\'g\'ri javob', help_text='Bu to\'g\'ri javobmi? (faqat bitta javob to\'g\'ri bo\'lishi kerak)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'answers'
        verbose_name = 'Javob'
        verbose_name_plural = 'Javoblar'

    def __str__(self):
        return f"{self.question} - {self.text[:50]}"


# 22. Foydalanuvchi kurs progressi
class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress', verbose_name='Foydalanuvchi')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress', verbose_name='Kurs')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Boshlangan vaqt')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Tugatilgan vaqt')
    is_completed = models.BooleanField(default=False, verbose_name='Tugatilgan')
    test_score = models.IntegerField(blank=True, null=True, verbose_name='Test natijasi (foiz)')
    test_passed = models.BooleanField(default=False, verbose_name='Test o\'tdi')

    class Meta:
        db_table = 'user_course_progress'
        verbose_name = 'Foydalanuvchi kurs progressi'
        verbose_name_plural = 'Foydalanuvchi kurs progresslari'
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user} - {self.course.name}"


# 23. Foydalanuvchi modul progressi
class UserModuleProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress', verbose_name='Foydalanuvchi')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_progress', verbose_name='Modul')
    viewed_presentation = models.BooleanField(default=False, verbose_name='Taqdimot ko\'rildi')
    watched_video = models.BooleanField(default=False, verbose_name='Video ko\'rildi')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Tugatilgan vaqt')
    is_completed = models.BooleanField(default=False, verbose_name='Tugatilgan')

    class Meta:
        db_table = 'user_module_progress'
        verbose_name = 'Foydalanuvchi modul progressi'
        verbose_name_plural = 'Foydalanuvchi modul progresslari'
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user} - {self.module}"


# 24. Test natijalari
class UserTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results', verbose_name='Foydalanuvchi')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='test_results', verbose_name='Kurs')
    score = models.IntegerField(verbose_name='Ball')
    total_questions = models.IntegerField(verbose_name='Jami savollar')
    correct_answers = models.IntegerField(verbose_name='To\'g\'ri javoblar')
    percentage = models.IntegerField(verbose_name='Foiz')
    passed = models.BooleanField(default=False, verbose_name='O\'tdi')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Topshirilgan vaqt')

    class Meta:
        db_table = 'user_test_results'
        verbose_name = 'Test natijasi'
        verbose_name_plural = 'Test natijalari'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user} - {self.course.name} - {self.percentage}%"


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates', verbose_name='Foydalanuvchi')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates', verbose_name='Kurs')
    test_result = models.OneToOneField(UserTestResult, on_delete=models.CASCADE, related_name='certificate', verbose_name='Test natijasi')
    certificate_file = models.FileField(upload_to='certificates/', verbose_name='Sertifikat fayli')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Berilgan vaqt')
    
    class Meta:
        db_table = 'certificates'
        verbose_name = 'Sertifikat'
        verbose_name_plural = 'Sertifikatlar'
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.user} - {self.course.name} sertifikati"


# 25. Saralash testi (Assessment Test)
class AssessmentTest(models.Model):
    title = models.CharField(max_length=255, default='Iqtidorli talabamisiz?', verbose_name='Test nomi', help_text='Saralash testi nomini kiriting')
    description = models.TextField(verbose_name='Test haqida ma\'lumot', help_text='Test haqida batafsil ma\'lumot va ko\'rsatmalar')
    test_set = models.ForeignKey('TestSet', on_delete=models.SET_NULL, null=True, blank=True, related_name='assessment_tests', verbose_name='Test to\'plami', help_text='Tayyor test to\'plamini tanlang')
    time_limit = models.IntegerField(default=60, verbose_name='Vaqt limiti (daqiqalarda)', help_text='Test uchun berilgan vaqt (daqiqalarda, masalan: 60)')
    pass_percentage = models.IntegerField(default=60, verbose_name='O\'tish foizi', help_text='Testni o\'tish uchun minimal foiz (masalan: 60)')
    retry_delay_hours = models.IntegerField(default=1, verbose_name='Qayta urinish uchun kutish vaqti (soatlarda)', help_text='Testni qayta topshirish uchun kutish vaqti (soatlarda, masalan: 1)')
    is_active = models.BooleanField(default=True, verbose_name='Faol', help_text='Test faolmi? (belgilangan bo\'lsa, foydalanuvchilar ko\'radi)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessment_tests'
        verbose_name = 'Saralash testi'
        verbose_name_plural = 'Saralash testlari'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


# 26. Saralash testi natijalari
class AssessmentTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_results', verbose_name='Foydalanuvchi')
    assessment_test = models.ForeignKey(AssessmentTest, on_delete=models.CASCADE, related_name='results', verbose_name='Saralash testi')
    score = models.IntegerField(verbose_name='Ball')
    total_questions = models.IntegerField(verbose_name='Jami savollar')
    correct_answers = models.IntegerField(verbose_name='To\'g\'ri javoblar')
    percentage = models.FloatField(verbose_name='Foiz')
    passed = models.BooleanField(default=False, verbose_name='O\'tdi')
    time_taken = models.IntegerField(null=True, blank=True, verbose_name='Sarflangan vaqt (soniyalarda)')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Topshirilgan vaqt')
    
    class Meta:
        db_table = 'assessment_test_results'
        verbose_name = 'Saralash testi natijasi'
        verbose_name_plural = 'Saralash testi natijalari'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user} - {self.assessment_test.title} - {self.percentage}%"
        verbose_name_plural = 'Sertifikatlar'
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"{self.user} - {self.course.name} sertifikati"

