import re

from django.db import migrations, models


def _phone_digits(value):
    digits = re.sub(r'\D', '', str(value or ''))
    if digits.startswith('998') and len(digits) >= 12:
        return digits[3:12]
    if len(digits) >= 9:
        return digits[-9:]
    return digits


def clean_user_contacts(apps, schema_editor):
    User = apps.get_model('main', 'User')
    seen_emails = set()
    seen_phones = set()
    for user in User.objects.all().order_by('id'):
        email = (user.email or '').strip().lower()
        if not email or email in seen_emails:
            new_email = None
        else:
            new_email = email
            seen_emails.add(email)

        raw = (user.phone_number or '').strip()
        digits = _phone_digits(raw)
        if len(digits) == 9:
            compact = f'+998{digits}'
        else:
            compact = raw or None

        if not compact or compact in seen_phones:
            new_phone = None
        else:
            new_phone = compact
            seen_phones.add(compact)

        User.objects.filter(pk=user.pk).update(email=new_email, phone_number=new_phone)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_student_activity_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='education_direction',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name="Ta'lim yo'nalishi"),
        ),
        migrations.AddField(
            model_name='user',
            name='education_stage',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name="Ta'lim bosqichi / kurs"),
        ),
        migrations.CreateModel(
            name='OlympiadProgramCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(help_text='Lotin harflar, masalan: biologiya, geografiya. 8 ta asosiy kodni takrorlamang.', max_length=50, unique=True, verbose_name='Kod')),
                ('title', models.CharField(max_length=255, verbose_name='Nomi')),
                ('icon_class', models.CharField(default='fas fa-medal', help_text='Masalan: fas fa-leaf', max_length=80, verbose_name='Ikonka (Font Awesome)')),
                ('order', models.PositiveIntegerField(default=9, verbose_name='Tartib')),
                ('is_active', models.BooleanField(default=True, verbose_name='Faol')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Olimpiada dasturi kodi',
                'verbose_name_plural': 'Olimpiada dasturlari kodlari',
                'db_table': 'olympiad_program_codes',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AlterField(
            model_name='olympiadprogram',
            name='code',
            field=models.CharField(max_length=50, unique=True, verbose_name='Olimpiada kodi'),
        ),
        migrations.RunPython(clean_user_contacts, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, help_text="Ixtiyoriy. Agar kiritilsa, takrorlanmasligi kerak.", max_length=254, null=True, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Login uchun ishlatiladi', max_length=20, null=True, unique=True, verbose_name='Telefon raqam'),
        ),
    ]
