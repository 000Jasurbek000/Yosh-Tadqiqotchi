"""Demo ma'lumotlar: 2 ta olimpiada dasturi + topshiriq fayllari."""
import os
from django.conf import settings
from django.db import migrations


DEMO_MATH_FILE = """XALQARO MATEMATIKA OLIMPIADASI — NAMUNAVIY TOPSHIRIQLAR
============================================================

1-savol (Algebra)
-----------------
n natural son uchun isbotlang:
    n^5 - n soni 30 ga karralidir.

2-savol (Geometriya)
--------------------
ABC uchburchakda AB = 13, BC = 14, AC = 15. Uchburchakning
ichkari aylanasi radiusini va tashqi aylanasi radiusini toping.

3-savol (Sonlar nazariyasi)
---------------------------
Hech qaysi raqami nolga teng bo'lmagan necha xil natural son
mavjud bo'lib, ularning raqamlari yig'indisi 25 ga teng?

4-savol (Kombinatorika)
-----------------------
8 ta turli kitobni 3 ta o'quvchiga necha xil usulda
taqsimlash mumkin (har bir o'quvchi kamida 1 ta kitob olishi shart)?

5-savol (Trigonometriya)
------------------------
sin(x) + cos(x) = 1/2 bo'lsa, sin(x) - cos(x) ning qiymatini toping.

============================================================
TAVSIYA QILINGAN ADABIYOT:
1. Polya G. — "Matematik kashfiyot"
2. Yaglom I. — "Geometricheskiye zadachi"
3. Andreyev V. — "Olimpiada matematikasi"
"""


DEMO_IT_FILE = """XALQARO IT OLIMPIADASI — NAMUNAVIY TOPSHIRIQLAR
============================================================

1-vazifa (Algoritmlar)
----------------------
Berilgan N ta sondan iborat massivda eng uzun ortib boruvchi
qismiy ketma-ketlikni toping. Algoritm O(N log N) vaqtda
bajarilishi kerak.

Kirish: 10 22 9 33 21 50 41 60
Chiqish: 5 (masalan: 10, 22, 33, 50, 60)


2-vazifa (Ma'lumotlar tuzilmasi)
--------------------------------
Stack (LIFO) ma'lumot tuzilmasini ikkita queue yordamida
amalga oshiring. Push va pop operatsiyalarining amortizatsion
murakkabligini hisoblang.


3-vazifa (Dinamik dasturlash)
-----------------------------
Sayohatchi savdogar muammosini dinamik dasturlash usulida
yeching (Held-Karp algoritmi). N = 20 ta shahar uchun.


4-vazifa (Graflar)
------------------
Yo'naltirilmagan grafda qattiq bog'langan komponentlar sonini
toping. Tarjan algoritmi yoki Kosaraju algoritmidan foydalaning.


5-vazifa (Amaliy dasturlash)
----------------------------
Python yoki C++ tilida REST API yarating:
- POST /api/users — yangi foydalanuvchi
- GET  /api/users — barchasini olish
- GET  /api/users/{id} — bittasini olish
- PUT  /api/users/{id} — yangilash
- DELETE /api/users/{id} — o'chirish
JSON formatda javob qaytarsin.

============================================================
TAVSIYA QILINGAN MANBALAR:
1. Cormen et al. — "Introduction to Algorithms"
2. Skiena S. — "The Algorithm Design Manual"
3. codeforces.com, leetcode.com — onlayn mashqlar
"""


def create_demo_programs(apps, schema_editor):
    OlympiadProgram = apps.get_model('main', 'OlympiadProgram')

    tasks_dir = os.path.join(settings.MEDIA_ROOT, 'olympiad_tasks')
    os.makedirs(tasks_dir, exist_ok=True)

    # 1) Matematika
    math_path = os.path.join(tasks_dir, 'matematika_namunaviy_topshiriqlar.txt')
    with open(math_path, 'w', encoding='utf-8') as f:
        f.write(DEMO_MATH_FILE)

    OlympiadProgram.objects.update_or_create(
        code='matematika',
        defaults={
            'title': "Xalqaro matematika fan olimpiadalariga tayyorlov",
            'short_intro': (
                "Xalqaro matematika olimpiadalari — talabalarning mantiqiy "
                "fikrlash, masala yechish va matematik tahlil qobiliyatlarini "
                "sinaydi. Ushbu dasturda siz IMO (International Mathematical Olympiad), "
                "IMC va respublika miqyosidagi tanlovlarga tayyorgarlik ko'rasiz."
            ),
            'required_skills': (
                "• Algebra (tenglamalar, ko'phadlar, almashtirishlar)\n"
                "• Geometriya (planimetriya, stereometriya, trigonometriya)\n"
                "• Sonlar nazariyasi (bo'linish, sodda sonlar, modular arifmetika)\n"
                "• Kombinatorika va graflar nazariyasi asoslari\n"
                "• Matematik induksiya va isbotlash texnikasi\n"
                "• Matematik kitoblar bilan mustaqil ishlash"
            ),
            'knowledge_areas': (
                "1. Klassik algebra: ko'phadlar, ratsional sonlar, irratsional ifodalar\n"
                "2. Elementar geometriya: o'xshashlik, vektorlar, koordinatalar metodi\n"
                "3. Trigonometriya: o'zgartirishlar, tenglamalar, identlik\n"
                "4. Sonlar nazariyasi: Diofant tenglamalari, Fermat teoremasi\n"
                "5. Kombinatorika: o'rin almashtirish, Inkluziya-Eksklyuziya printsipi\n"
                "6. Tengsizliklar: AM-GM, Koshi-Bunyakovskiy, Yensen tengsizligi"
            ),
            'self_check_text': (
                "Quyidagi savollarga javob bera olsangiz — bu olimpiadaga "
                "tayyor ekansiz:\n\n"
                "1) n^5 - n soni har qanday n natural soni uchun 30 ga karralimi?\n"
                "2) ABC uchburchakda AB=13, BC=14, AC=15. Ichki aylana radiusi qancha?\n"
                "3) Necha xil natural son raqamlari yig'indisi 25 ga teng (raqamlar ≠ 0)?\n"
                "4) sin(x) + cos(x) = 1/2 bo'lsa, sin(x) - cos(x) qancha?\n\n"
                "Batafsil topshiriqlar uchun pastdagi PDF/Word faylni yuklab oling."
            ),
            'task_file': 'olympiad_tasks/matematika_namunaviy_topshiriqlar.txt',
            'additional_info': (
                "Tayyorgarlik kurslari hafta sigfra 3 marta o'tkaziladi. "
                "Onlayn va oflayn formatlar mavjud. Saralash testidan o'tgan "
                "iqtidorli talabalar uchun bepul."
            ),
            'is_active': True,
        }
    )

    # 2) IT
    it_path = os.path.join(tasks_dir, 'it_namunaviy_topshiriqlar.txt')
    with open(it_path, 'w', encoding='utf-8') as f:
        f.write(DEMO_IT_FILE)

    OlympiadProgram.objects.update_or_create(
        code='it',
        defaults={
            'title': "Xalqaro IT olimpiadalariga tayyorlov",
            'short_intro': (
                "ACM ICPC, IOI (International Olympiad in Informatics), "
                "Google Code Jam va boshqa xalqaro IT tanlovlariga "
                "tayyorlov. Algoritmlar, ma'lumotlar tuzilmasi, dinamik "
                "dasturlash va amaliy dasturlash mahoratingizni rivojlantiring."
            ),
            'required_skills': (
                "• Asosiy dasturlash tillaridan kamida bittasi (C++, Python, Java)\n"
                "• Algoritmik fikrlash va vaqt murakkabligi tahlili\n"
                "• Ma'lumotlar tuzilmalari: massiv, ro'yxat, stek, navbat, daraxt, graf\n"
                "• Saralash va qidirish algoritmlari\n"
                "• Dinamik dasturlash (DP) — kamida 2-pog'ona\n"
                "• Inglish tilida texnik adabiyotlarni o'qish qobiliyati"
            ),
            'knowledge_areas': (
                "1. Asosiy algoritmlar: saralash, qidirish, rekursiya\n"
                "2. Ma'lumotlar tuzilmasi: bog'langan ro'yxat, daraxt, heap, hash\n"
                "3. Graflar nazariyasi: BFS, DFS, Dijkstra, Floyd-Warshall, MST\n"
                "4. Dinamik dasturlash va memoization\n"
                "5. Matnlar bilan ishlash: KMP, suffix array, Z-funktsiya\n"
                "6. Geometrik algoritmlar: convex hull, segmentlar kesishishi\n"
                "7. Sonlar nazariyasi algoritmlar: Eratosfen, GCD, modular arifmetika"
            ),
            'self_check_text': (
                "Bu olimpiadaga tayyor bo'lish uchun quyidagilarni bilishingiz kerak:\n\n"
                "1) Eng uzun ortib boruvchi qismiy ketma-ketlik (LIS) — O(N log N)\n"
                "2) Stack ni ikki queue bilan amalga oshirish\n"
                "3) Held-Karp algoritmi (TSP DP yechimi)\n"
                "4) Tarjan SCC algoritmi\n"
                "5) REST API yaratish (Python Flask / FastAPI yoki Node.js)\n\n"
                "Batafsil topshiriqlar uchun pastdagi faylni yuklab oling."
            ),
            'task_file': 'olympiad_tasks/it_namunaviy_topshiriqlar.txt',
            'additional_info': (
                "Tayyorgarlik onlayn olib boriladi: codeforces.com va leetcode.com "
                "platformalarida amaliy mashqlar. Haftada 2 ta kontest va "
                "har shanba kuni jonli analizi mavjud."
            ),
            'is_active': True,
        }
    )


def reverse_demo(apps, schema_editor):
    OlympiadProgram = apps.get_model('main', 'OlympiadProgram')
    OlympiadProgram.objects.filter(code__in=['matematika', 'it']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0023_olympiadprogram_olympiadapplication'),
    ]
    operations = [
        migrations.RunPython(create_demo_programs, reverse_demo),
    ]
