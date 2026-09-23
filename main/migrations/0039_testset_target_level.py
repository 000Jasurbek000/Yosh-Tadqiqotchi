from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_seed_olympiad_program_codes'),
    ]

    operations = [
        migrations.AddField(
            model_name='testset',
            name='target_level',
            field=models.CharField(
                blank=True,
                choices=[
                    ('1-kurs', '1-kurs (bakalavr)'),
                    ('2-kurs', '2-kurs (bakalavr)'),
                    ('3-kurs', '3-kurs (bakalavr)'),
                    ('4-kurs', '4-kurs (bakalavr)'),
                    ('magistr', 'Magistr'),
                ],
                default='',
                help_text="Bakalavr: 1–4 kurs. Magistr: bitta to'plam (kursdan qat'i nazar). PhD/DSc uchun kerak emas.",
                max_length=20,
                verbose_name='Kim uchun',
            ),
        ),
    ]
