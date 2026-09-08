"""Platforma ma'lumotlarini KnowledgeChunk ga indekslash."""
import re
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from main.models import (
    KnowledgeChunk,
    StateScholarship, BuxduScholarship, BuxduWinnerDatabase,
    Olympiad, BuxduOlympiad, Conference, ResearcherRegulation,
    Literature, Course, Module, Announcement, OakDatabase,
    DissertationBank, ArticleBank, TalentedStudentDatabase,
    ScientificSupervisor, OlympiadProgram, AssessmentTest, Survey,
)
from .text_utils import normalize_text, tokenize, content_hash


def _upsert_chunk(**kwargs):
    """object_id bo'yicha yangilash yoki yaratish (title o'zgarsa ham bir xil chunk)."""
    source_type = kwargs['source_type']
    object_id = kwargs.get('object_id', '')
    title = kwargs['title']
    content = kwargs['content']
    ch = content_hash(title, content, source_type, object_id)

    tokens = tokenize(f"{title} {content} {kwargs.get('category', '')}")
    search_text = ' '.join(tokens)

    existing = None
    if object_id:
        existing = KnowledgeChunk.objects.filter(
            source_type=source_type,
            object_id=object_id,
        ).first()
    if existing is None:
        existing = KnowledgeChunk.objects.filter(
            source_type=source_type,
            object_id=object_id,
            title=title,
        ).first()

    defaults = {
        'title': title,
        'content': content,
        'url': kwargs.get('url', ''),
        'category': kwargs.get('category', ''),
        'source_file': kwargs.get('source_file', ''),
        'priority': kwargs.get('priority', 50),
        'content_hash': ch,
        'search_text': search_text,
        'is_active': True,
    }

    if existing:
        if existing.content_hash == ch and existing.title == title:
            return False  # o'zgarmagan
        for k, v in defaults.items():
            setattr(existing, k, v)
        existing.save()
        return True

    KnowledgeChunk.objects.create(
        source_type=source_type,
        object_id=object_id,
        **defaults,
    )
    return True


def _delete_chunks_by_object_id(object_id: str):
    if not object_id:
        return 0
    deleted, _ = KnowledgeChunk.objects.filter(object_id=object_id).delete()
    return deleted


def index_instance(instance) -> bool:
    """Bitta model obyektini knowledge base ga yozish. True = yangilandi/yaratildi."""
    from main.models import (
        StateScholarship, BuxduScholarship, BuxduWinnerDatabase,
        Olympiad, BuxduOlympiad, Conference, ResearcherRegulation,
        Literature, Course, Announcement, OakDatabase,
        DissertationBank, ArticleBank, TalentedStudentDatabase,
        ScientificSupervisor, OlympiadProgram, AssessmentTest, Survey,
    )

    if isinstance(instance, StateScholarship):
        return _upsert_chunk(
            source_type='database',
            title=f'Davlat stipendiyasi: {instance.name}',
            content=(
                f"Davlat stipendiyasi: {instance.name}. "
                f"Tavsif: {instance.short_description or '—'}. "
                f"Nizom: {'havola/fayl mavjud' if (instance.regulation_link or instance.regulation_file) else 'yo\'q'}. "
                f"Ariza: {instance.application_link or 'havola yo\'q'}."
            ),
            url='/davlat-stipendiyalari/',
            category='scholarship',
            object_id=f'state_scholarship:{instance.pk}',
            priority=90,
        )

    if isinstance(instance, BuxduScholarship):
        return _upsert_chunk(
            source_type='database',
            title=f'BuxDU stipendiyasi: {instance.name}',
            content=(
                f"BuxDU stipendiyasi: {instance.name}. "
                f"Tavsif: {instance.short_description or '—'}. "
                f"Ariza: {instance.application_link or 'havola yo\'q'}."
            ),
            url='/buxdu-stipendiyalari/',
            category='scholarship',
            object_id=f'buxdu_scholarship:{instance.pk}',
            priority=90,
        )

    if isinstance(instance, BuxduWinnerDatabase):
        return _upsert_chunk(
            source_type='database',
            title=f'Sovrindorlar bazasi: {instance.scholarship_type} ({instance.academic_year})',
            content=(
                f"BuxDU stipendiya sovrindorlari bazasi: {instance.scholarship_type}, "
                f"o'quv yili: {instance.academic_year}, fayl: {instance.file_name}."
            ),
            url='/buxdu-stipendiya-bazasi/',
            category='scholarship',
            object_id=f'buxdu_winner_db:{instance.pk}',
            priority=70,
        )

    if isinstance(instance, Olympiad):
        return _upsert_chunk(
            source_type='database',
            title=f'Olimpiada: {instance.name}',
            content=(
                f"Olimpiada: {instance.name}. Fan: {instance.subject}. Davlat: {instance.country}. "
                f"Turi: {instance.get_type_display() if hasattr(instance, 'get_type_display') else instance.type}. "
                f"Sana: {instance.date}. Tavsif: {instance.short_description or '—'}. "
                f"Ro'yxatdan o'tish: {instance.registration_link or 'havola yo\'q'}."
            ),
            url='/olimpiadalar/',
            category='olympiad',
            object_id=f'olympiad:{instance.pk}',
            priority=85,
        )

    if isinstance(instance, BuxduOlympiad):
        return _upsert_chunk(
            source_type='database',
            title=f'BuxDU olimpiadasi: {instance.subject}',
            content=(
                f"BuxDU olimpiadasi: {instance.subject}. Sana: {instance.date}. "
                f"Tavsif: {instance.description or '—'}. "
                f"Status: {'tugagan' if instance.is_finished else 'kutilmoqda'}."
            ),
            url='/buxdu-olimpiadalari/',
            category='olympiad',
            object_id=f'buxdu_olympiad:{instance.pk}',
            priority=85,
        )

    if isinstance(instance, OlympiadProgram):
        if not instance.is_active:
            _delete_chunks_by_object_id(f'olympiad_program:{instance.pk}')
            return True
        return _upsert_chunk(
            source_type='database',
            title=f'Olimpiada dasturi: {instance.title}',
            content=(
                f"Olimpiada dasturi (Iqtidor Yo'li): {instance.title}. "
                f"Kirish: {instance.short_intro or '—'}. "
                f"Kerakli ko'nikmalar: {instance.required_skills or '—'}. "
                f"Bilim sohalari: {instance.knowledge_areas or '—'}. "
                f"O'z-o'zini tekshirish: {instance.self_check_text or '—'}."
            ),
            url=f'/olimpiada/{instance.code}/',
            category='olympiad',
            object_id=f'olympiad_program:{instance.pk}',
            priority=88,
        )

    if isinstance(instance, Conference):
        return _upsert_chunk(
            source_type='database',
            title=f'Konferensiya: {instance.name}',
            content=(
                f"Konferensiya: {instance.name}. "
                f"Turi: {instance.get_type_display() if hasattr(instance, 'get_type_display') else instance.type}."
            ),
            url='/xalqaro-konferensiyalar/',
            category='conference',
            object_id=f'conference:{instance.pk}',
            priority=75,
        )

    if isinstance(instance, ResearcherRegulation):
        return _upsert_chunk(
            source_type='database',
            title=f'Nizom: {instance.regulation_name}',
            content=f"Ilmiy tadqiqotchilar uchun nizom: {instance.regulation_name}.",
            url='/ilmiy-nizomlar/',
            category='regulation',
            object_id=f'regulation:{instance.pk}',
            priority=80,
        )

    if isinstance(instance, Literature):
        return _upsert_chunk(
            source_type='database',
            title=f'Adabiyot: {instance.title}',
            content=(
                f"Adabiyot: {instance.title}. Muallif: {instance.author}. "
                f"Soha: {instance.get_field_display() if instance.field else '—'}. "
                f"Tavsif: {instance.description or '—'}."
            ),
            url='/adabiyotlar/',
            category='literature',
            object_id=f'literature:{instance.pk}',
            priority=70,
        )

    if isinstance(instance, Course):
        if not instance.is_active:
            _delete_chunks_by_object_id(f'course:{instance.pk}')
            return True
        return _upsert_chunk(
            source_type='database',
            title=f'Kurs: {instance.name}',
            content=(
                f"Kurs: {instance.name}. Tavsif: {instance.short_description or '—'}. "
                f"Modullar soni: {instance.module_count}. O'tish bali: {instance.passing_score}."
            ),
            url='/courses/',
            category='course',
            object_id=f'course:{instance.pk}',
            priority=85,
        )

    if isinstance(instance, Announcement):
        return _upsert_chunk(
            source_type='database',
            title=f"E'lon: {instance.title}",
            content=(
                f"E'lon: {instance.title}. Muallif: {instance.author}. "
                f"Sana: {instance.date}. {instance.short_text or ''} {instance.detailed_text or ''}"
            )[:2000],
            url='/',
            category='announcement',
            object_id=f'announcement:{instance.pk}',
            priority=65,
        )

    if isinstance(instance, OakDatabase):
        return _upsert_chunk(
            source_type='database',
            title=f'Jurnal: {instance.journal_name}',
            content=f"OAK jurnali: {instance.journal_name}. Turi: {instance.type}. Yo'nalishlar: {instance.fields}.",
            url='/mahalliy-oak-jurnallari/',
            category='journal',
            object_id=f'oak:{instance.pk}',
            priority=70,
        )

    if isinstance(instance, DissertationBank):
        return _upsert_chunk(
            source_type='database',
            title=f'Dissertatsiya: {instance.database_type}',
            content=f"Dissertatsiya banki: {instance.database_type}, yo'nalish: {instance.direction}.",
            url='/dissertatsiyalar-banki/',
            category='dissertation',
            object_id=f'diss:{instance.pk}',
            priority=65,
        )

    if isinstance(instance, ArticleBank):
        return _upsert_chunk(
            source_type='database',
            title=f'Maqola banki: {instance.name}',
            content=f"Maqola banki: {instance.name}. Qo'llanma: {instance.short_guide or '—'}.",
            url='/maqolalar-banki/',
            category='article',
            object_id=f'article:{instance.pk}',
            priority=65,
        )

    if isinstance(instance, TalentedStudentDatabase):
        return _upsert_chunk(
            source_type='database',
            title=f'Iqtidorli talabalar bazasi ({instance.academic_year})',
            content=f"Iqtidorli talabalar bazasi: {instance.academic_year}, {instance.file_name}.",
            url='/iqtidorli-baza/',
            category='talent',
            object_id=f'talent_db:{instance.pk}',
            priority=75,
        )

    if isinstance(instance, ScientificSupervisor):
        if not instance.is_active:
            _delete_chunks_by_object_id(f'supervisor:{instance.pk}')
            return True
        return _upsert_chunk(
            source_type='database',
            title=f'Ilmiy rahbar: {instance.full_name}',
            content=(
                f"Ilmiy rahbar: {instance.full_name}. Lavozim: {instance.position}. "
                f"Mutaxassislik: {instance.specialty}. "
                f"Telefon: {instance.phone or '—'}. Email: {instance.email or '—'}."
            ),
            url='/ilmiy-rahbarlar/',
            category='supervisor',
            object_id=f'supervisor:{instance.pk}',
            priority=80,
        )

    if isinstance(instance, AssessmentTest):
        if not instance.is_active:
            _delete_chunks_by_object_id(f'assessment:{instance.pk}')
            return True
        return _upsert_chunk(
            source_type='database',
            title='Saralash testi (Assessment)',
            content=(
                f"Saralash testi: {instance.title}. Tavsif: {instance.description or '—'}. "
                f"Vaqt limiti: {instance.time_limit} daqiqa. O'tish foizi: {instance.pass_percentage}%. "
                f"Qayta urinish kechikishi: {instance.retry_delay_hours} soat."
            ),
            url='/assessment-test/',
            category='assessment',
            object_id=f'assessment:{instance.pk}',
            priority=95,
        )

    if isinstance(instance, Survey):
        if not instance.is_active:
            _delete_chunks_by_object_id(f'survey:{instance.pk}')
            return True
        return _upsert_chunk(
            source_type='database',
            title=f"So'rovnoma: {instance.title}",
            content=f"So'rovnoma: {instance.title}. {instance.description or ''} Havola: {instance.link or '—'}.",
            url='/iqtidorli-sorovnoma/',
            category='survey',
            object_id=f'survey:{instance.pk}',
            priority=60,
        )

    return False


def object_id_for_instance(instance) -> str:
    mapping = {
        'StateScholarship': 'state_scholarship',
        'BuxduScholarship': 'buxdu_scholarship',
        'BuxduWinnerDatabase': 'buxdu_winner_db',
        'Olympiad': 'olympiad',
        'BuxduOlympiad': 'buxdu_olympiad',
        'OlympiadProgram': 'olympiad_program',
        'Conference': 'conference',
        'ResearcherRegulation': 'regulation',
        'Literature': 'literature',
        'Course': 'course',
        'Announcement': 'announcement',
        'OakDatabase': 'oak',
        'DissertationBank': 'diss',
        'ArticleBank': 'article',
        'TalentedStudentDatabase': 'talent_db',
        'ScientificSupervisor': 'supervisor',
        'AssessmentTest': 'assessment',
        'Survey': 'survey',
    }
    prefix = mapping.get(instance.__class__.__name__)
    if not prefix or not instance.pk:
        return ''
    return f'{prefix}:{instance.pk}'


def delete_instance_chunks(instance) -> int:
    oid = object_id_for_instance(instance)
    return _delete_chunks_by_object_id(oid)


def _strip_html_template(raw: str) -> str:
    """Template'dan foydali matnni ajratish (taglar, script, style olib tashlash)."""
    raw = re.sub(r'{%.*?%}', ' ', raw, flags=re.DOTALL)
    raw = re.sub(r'{{.*?}}', ' ', raw, flags=re.DOTALL)
    raw = re.sub(r'<script[^>]*>.*?</script>', ' ', raw, flags=re.DOTALL | re.I)
    raw = re.sub(r'<style[^>]*>.*?</style>', ' ', raw, flags=re.DOTALL | re.I)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    raw = re.sub(r'&nbsp;|&amp;|&lt;|&gt;|&quot;', ' ', raw)
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw


# ─── Database sources ───────────────────────────────────────────────────────

def index_scholarships():
    count = 0
    for s in StateScholarship.objects.all():
        content = (
            f"Davlat stipendiyasi: {s.name}. "
            f"Tavsif: {s.short_description or '—'}. "
            f"Nizom: {'havola/fayl mavjud' if (s.regulation_link or s.regulation_file) else 'yo\'q'}. "
            f"Ariza: {s.application_link or 'havola yo\'q'}."
        )
        if _upsert_chunk(
            source_type='database',
            title=f'Davlat stipendiyasi: {s.name}',
            content=content,
            url='/davlat-stipendiyalari/',
            category='scholarship',
            object_id=f'state_scholarship:{s.pk}',
            priority=90,
        ):
            count += 1

    for s in BuxduScholarship.objects.all():
        content = (
            f"BuxDU stipendiyasi: {s.name}. "
            f"Tavsif: {s.short_description or '—'}. "
            f"Ariza: {s.application_link or 'havola yo\'q'}."
        )
        if _upsert_chunk(
            source_type='database',
            title=f'BuxDU stipendiyasi: {s.name}',
            content=content,
            url='/buxdu-stipendiyalari/',
            category='scholarship',
            object_id=f'buxdu_scholarship:{s.pk}',
            priority=90,
        ):
            count += 1

    for db in BuxduWinnerDatabase.objects.all():
        content = (
            f"BuxDU stipendiya sovrindorlari bazasi: {db.scholarship_type}, "
            f"o'quv yili: {db.academic_year}, fayl: {db.file_name}."
        )
        if _upsert_chunk(
            source_type='database',
            title=f'Sovrindorlar bazasi: {db.scholarship_type} ({db.academic_year})',
            content=content,
            url='/buxdu-stipendiya-bazasi/',
            category='scholarship',
            object_id=f'buxdu_winner_db:{db.pk}',
            priority=70,
        ):
            count += 1
    return count


def index_olympiads():
    count = 0
    for o in Olympiad.objects.all():
        content = (
            f"Olimpiada: {o.name}. Fan: {o.subject}. Davlat: {o.country}. "
            f"Turi: {o.get_type_display() if hasattr(o, 'get_type_display') else o.type}. "
            f"Sana: {o.date}. Tavsif: {o.short_description or '—'}. "
            f"Ro'yxatdan o'tish: {o.registration_link or 'havola yo\'q'}."
        )
        if _upsert_chunk(
            source_type='database',
            title=f'Olimpiada: {o.name}',
            content=content,
            url='/olimpiadalar/',
            category='olympiad',
            object_id=f'olympiad:{o.pk}',
            priority=85,
        ):
            count += 1

    for o in BuxduOlympiad.objects.all():
        content = (
            f"BuxDU olimpiadasi: {o.subject}. Sana: {o.date}. "
            f"Tavsif: {o.description or '—'}. "
            f"Status: {'tugagan' if o.is_finished else 'kutilmoqda'}."
        )
        if _upsert_chunk(
            source_type='database',
            title=f'BuxDU olimpiadasi: {o.subject}',
            content=content,
            url='/buxdu-olimpiadalari/',
            category='olympiad',
            object_id=f'buxdu_olympiad:{o.pk}',
            priority=85,
        ):
            count += 1

    for p in OlympiadProgram.objects.filter(is_active=True):
        content = (
            f"Olimpiada dasturi (Iqtidor Yo'li): {p.title}. "
            f"Kirish: {p.short_intro or '—'}. "
            f"Kerakli ko'nikmalar: {p.required_skills or '—'}. "
            f"Bilim sohalari: {p.knowledge_areas or '—'}. "
            f"O'z-o'zini tekshirish: {p.self_check_text or '—'}."
        )
        if _upsert_chunk(
            source_type='database',
            title=f'Olimpiada dasturi: {p.title}',
            content=content,
            url=f'/olimpiada/{p.code}/',
            category='olympiad',
            object_id=f'olympiad_program:{p.pk}',
            priority=88,
        ):
            count += 1
    return count


def index_other_db():
    count = 0
    for c in Conference.objects.all():
        content = f"Konferensiya: {c.name}. Turi: {c.get_type_display() if hasattr(c, 'get_type_display') else c.type}."
        if _upsert_chunk(
            source_type='database', title=f'Konferensiya: {c.name}', content=content,
            url='/xalqaro-konferensiyalar/', category='conference', object_id=f'conference:{c.pk}', priority=75,
        ):
            count += 1

    for r in ResearcherRegulation.objects.all():
        content = f"Ilmiy tadqiqotchilar uchun nizom: {r.regulation_name}."
        if _upsert_chunk(
            source_type='database', title=f'Nizom: {r.regulation_name}', content=content,
            url='/ilmiy-nizomlar/', category='regulation', object_id=f'regulation:{r.pk}', priority=80,
        ):
            count += 1

    for lit in Literature.objects.all():
        content = (
            f"Adabiyot: {lit.title}. Muallif: {lit.author}. "
            f"Soha: {lit.get_field_display() if lit.field else '—'}. "
            f"Tavsif: {lit.description or '—'}."
        )
        if _upsert_chunk(
            source_type='database', title=f'Adabiyot: {lit.title}', content=content,
            url='/adabiyotlar/', category='literature', object_id=f'literature:{lit.pk}', priority=70,
        ):
            count += 1

    for course in Course.objects.filter(is_active=True):
        content = (
            f"Kurs: {course.name}. Tavsif: {course.short_description or '—'}. "
            f"Modullar soni: {course.module_count}. O'tish bali: {course.passing_score}."
        )
        if _upsert_chunk(
            source_type='database', title=f'Kurs: {course.name}', content=content,
            url='/courses/', category='course', object_id=f'course:{course.pk}', priority=85,
        ):
            count += 1

    for a in Announcement.objects.all().order_by('-date')[:50]:
        content = f"E'lon: {a.title}. Muallif: {a.author}. Sana: {a.date}. {a.short_text or ''} {a.detailed_text or ''}"
        if _upsert_chunk(
            source_type='database', title=f"E'lon: {a.title}", content=content[:2000],
            url='/', category='announcement', object_id=f'announcement:{a.pk}', priority=65,
        ):
            count += 1

    for j in OakDatabase.objects.all():
        content = f"OAK jurnali: {j.journal_name}. Turi: {j.type}. Yo'nalishlar: {j.fields}."
        if _upsert_chunk(
            source_type='database', title=f'Jurnal: {j.journal_name}', content=content,
            url='/mahalliy-oak-jurnallari/', category='journal', object_id=f'oak:{j.pk}', priority=70,
        ):
            count += 1

    for d in DissertationBank.objects.all():
        content = f"Dissertatsiya banki: {d.database_type}, yo'nalish: {d.direction}."
        if _upsert_chunk(
            source_type='database', title=f'Dissertatsiya: {d.database_type}', content=content,
            url='/dissertatsiyalar-banki/', category='dissertation', object_id=f'diss:{d.pk}', priority=65,
        ):
            count += 1

    for art in ArticleBank.objects.all():
        content = f"Maqola banki: {art.name}. Qo'llanma: {art.short_guide or '—'}."
        if _upsert_chunk(
            source_type='database', title=f'Maqola banki: {art.name}', content=content,
            url='/maqolalar-banki/', category='article', object_id=f'article:{art.pk}', priority=65,
        ):
            count += 1

    for db in TalentedStudentDatabase.objects.all():
        content = f"Iqtidorli talabalar bazasi: {db.academic_year}, {db.file_name}."
        if _upsert_chunk(
            source_type='database', title=f'Iqtidorli talabalar bazasi ({db.academic_year})',
            content=content, url='/iqtidorli-baza/', category='talent',
            object_id=f'talent_db:{db.pk}', priority=75,
        ):
            count += 1

    for s in ScientificSupervisor.objects.filter(is_active=True):
        content = (
            f"Ilmiy rahbar: {s.full_name}. Lavozim: {s.position}. "
            f"Mutaxassislik: {s.specialty}. Telefon: {s.phone or '—'}. Email: {s.email or '—'}."
        )
        if _upsert_chunk(
            source_type='database', title=f'Ilmiy rahbar: {s.full_name}', content=content,
            url='/ilmiy-rahbarlar/', category='supervisor', object_id=f'supervisor:{s.pk}', priority=80,
        ):
            count += 1

    for t in AssessmentTest.objects.filter(is_active=True):
        content = (
            f"Saralash testi: {t.title}. Tavsif: {t.description or '—'}. "
            f"Vaqt limiti: {t.time_limit} daqiqa. O'tish foizi: {t.pass_percentage}%. "
            f"Qayta urinish kechikishi: {t.retry_delay_hours} soat."
        )
        if _upsert_chunk(
            source_type='database', title='Saralash testi (Assessment)', content=content,
            url='/assessment-test/', category='assessment', object_id=f'assessment:{t.pk}', priority=95,
        ):
            count += 1

    for sv in Survey.objects.filter(is_active=True):
        content = f"So'rovnoma: {sv.title}. {sv.description or ''} Havola: {sv.link or '—'}."
        if _upsert_chunk(
            source_type='database', title=f"So'rovnoma: {sv.title}", content=content,
            url='/iqtidorli-sorovnoma/', category='survey', object_id=f'survey:{sv.pk}', priority=60,
        ):
            count += 1

    return count


def index_business_logic():
    """Koddan foydalanuvchiga tegishli biznes qoidalarni tushuntirilgan shaklda."""
    chunks = [
        {
            'title': 'Iqtidorli talaba statusini olish',
            'content': (
                "Yosh Tadqiqotchi platformasida iqtidorli talaba statusini olish uchun "
                "Saralash testidan muvaffaqiyatli o'tish kerak. "
                "Test faol bo'lsa, menyudagi «Saralash testi» bo'limidan boshlang. "
                "Belgilangan foizdan yuqori natija olsangiz, profilingizda talaba holati "
                "Iqtidorli ga o'zgaradi; admin ham Talaba holatini Iqtidorli qilib belgilashi mumkin. "
                "Testni yiqilganingizda qayta topshirish uchun kutish vaqti (soatlar) qo'llaniladi. "
                "«Iqtidor Yo'li» va ba'zi olimpiada dasturlari faqat iqtidorli "
                "talabalar (yoki admin) uchun ochiq."
            ),
            'url': '/assessment-test/',
            'category': 'talent',
            'object_id': 'logic:iqtidorli_status',
            'priority': 100,
            'source_file': 'main/views.py (submit_assessment_test)',
        },
        {
            'title': 'Kurslar va modullar tartibi',
            'content': (
                "Platformadagi kurslar bir nechta moduldan iborat. Oddiy foydalanuvchi "
                "oldingi modulni tugatmaguncha keyingisini ocholmaydi. Har bir modulda "
                "video va/yoki PDF taqdimotni ko'rib, 'Modulni tugatdim' tugmasini bosish kerak. "
                "Barcha modullar tugagach kurs testi ochiladi. Testdan o'tish bali kurs "
                "sozlamalarida belgilangan. Muvaffaqiyatsiz urinishdan keyin qayta topshirish "
                "uchun kutish vaqti bor. Admin foydalanuvchilar bu cheklovlarni chetlab o'tadi."
            ),
            'url': '/courses/',
            'category': 'course',
            'object_id': 'logic:course_progress',
            'priority': 90,
            'source_file': 'main/views.py (CourseDetailView, course_test_view)',
        },
        {
            'title': 'Ro\'yxatdan o\'tish va rollar',
            'content': (
                "Ro'yxatdan o'tishda foydalanuvchi rolini tanlaydi: Talaba, Foydalanuvchi yoki "
                "O'qituvchi. Fakultet maydoni majburiy. Talaba holati (Oddiy / Iqtidorli) "
                "admin tomonidan yoki saralash testi orqali belgilanadi — ro'yxatdan o'tishda "
                "avtomatik iqtidorli berilmaydi."
            ),
            'url': '/register/',
            'category': 'account',
            'object_id': 'logic:registration',
            'priority': 80,
            'source_file': 'main/forms.py, main/models.py (User)',
        },
        {
            'title': 'Platforma bo\'limlari (umumiy)',
            'content': (
                "Yosh Tadqiqotchi (yoshtadqiqotchi.uz) — yosh tadqiqotchilar uchun platforma. "
                "Asosiy bo'limlar: Davlat stipendiyalari, BuxDU stipendiyalari, Olimpiadalar, "
                "Konferensiyalar, Ilmiy nizomlar, Kurslar, Adabiyotlar, OAK jurnallar bazasi, "
                "Dissertatsiya va maqola banklari, Ilmiy rahbarlar, Saralash testi, "
                "Iqtidor Yo'li, Iqtidorli talabalar bazasi, E'lonlar."
            ),
            'url': '/',
            'category': 'platform',
            'object_id': 'logic:platform_overview',
            'priority': 95,
            'source_file': 'main/urls.py',
        },
    ]
    count = 0
    for c in chunks:
        if _upsert_chunk(source_type='business_logic', **c):
            count += 1
    return count


TEMPLATE_PAGES = [
    ('platforma_haqida.html', '/platforma-haqida/', 'Platforma haqida', 'platform', 90),
    ('iqtidor_yoli.html', '/iqtidor-yoli/', "Iqtidor Yo'li", 'talent', 95),
    ('assessment_test.html', '/assessment-test/', 'Saralash testi sahifasi', 'assessment', 95),
    ('service.html', '/service/', 'Xizmatlar', 'service', 70),
    ('maqola_jurnal_tavsiyasi.html', '/maqola-jurnal-tavsiyasi/', 'Maqola jurnal tavsiyasi', 'article', 70),
    ('davlat_stipendiyalari.html', '/davlat-stipendiyalari/', 'Davlat stipendiyalari sahifasi', 'scholarship', 80),
    ('buxdu_stipendiyalari.html', '/buxdu-stipendiyalari/', 'BuxDU stipendiyalari sahifasi', 'scholarship', 80),
    ('olimpiadalar.html', '/olimpiadalar/', 'Olimpiadalar sahifasi', 'olympiad', 80),
]


def index_templates():
    base = Path(settings.BASE_DIR) / 'django_templates'
    count = 0
    for filename, url, title, category, priority in TEMPLATE_PAGES:
        path = base / filename
        if not path.exists():
            continue
        raw = path.read_text(encoding='utf-8', errors='ignore')
        text = _strip_html_template(raw)
        if len(text) < 40:
            continue
        # Chunklarga bo'lish
        chunks = [text[i:i + 1500] for i in range(0, min(len(text), 6000), 1400)]
        for idx, chunk in enumerate(chunks):
            if _upsert_chunk(
                source_type='website',
                title=f'{title}' + (f' (qism {idx + 1})' if idx else ''),
                content=chunk,
                url=url,
                category=category,
                object_id=f'template:{filename}:{idx}',
                source_file=f'django_templates/{filename}',
                priority=priority,
            ):
                count += 1
    return count


def rebuild_index(full=False):
    """Barcha manbalarni indekslash. full=True bo'lsa eski chunklarni tozalash."""
    if full:
        KnowledgeChunk.objects.all().delete()

    stats = {
        'scholarships': index_scholarships(),
        'olympiads': index_olympiads(),
        'other_db': index_other_db(),
        'business_logic': index_business_logic(),
        'templates': index_templates(),
    }
    stats['total_active'] = KnowledgeChunk.objects.filter(is_active=True).count()
    stats['indexed_at'] = timezone.now().isoformat()
    return stats
