from django.db import migrations, models


BUILTIN = [
    ('matematika', 1, 'Xalqaro matematika fan olimpiadalariga tayyorlov', 'fas fa-square-root-variable'),
    ('kimyo', 2, 'Xalqaro kimyo fan olimpiadalariga tayyorlov', 'fas fa-flask'),
    ('ingliz_tili', 3, 'Xalqaro ingliz tili fan olimpiadalariga tayyorlov', 'fas fa-language'),
    ('falsafa', 4, 'Xalqaro falsafa fan olimpiadasiga tayyorlov', 'fas fa-brain'),
    ('iqtisodiyot', 5, 'Xalqaro iqtisodiyotga oid fanlar olimpiadasiga tayyorlov', 'fas fa-chart-line'),
    ('fizika', 6, 'Xalqaro fizika fan olimpiadasiga tayyorlov', 'fas fa-atom'),
    ('it', 7, 'Xalqaro IT olimpiadalariga tayyorlov', 'fas fa-laptop-code'),
    ('innovatsiya', 8, 'Xalqaro ilmiy-innovatsion mazmundagi tanlovlarga tayyorlov', 'fas fa-lightbulb'),
]


def seed_builtin_codes(apps, schema_editor):
    OlympiadProgramCode = apps.get_model('main', 'OlympiadProgramCode')
    for code, order, title, icon in BUILTIN:
        OlympiadProgramCode.objects.update_or_create(
            code=code,
            defaults={
                'order': order,
                'title': title,
                'icon_class': icon,
                'is_active': True,
            },
        )


def unseed_builtin_codes(apps, schema_editor):
    OlympiadProgramCode = apps.get_model('main', 'OlympiadProgramCode')
    OlympiadProgramCode.objects.filter(code__in=[row[0] for row in BUILTIN]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_phone_login_education_olympiad_codes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='olympiadprogramcode',
            name='code',
            field=models.SlugField(blank=True, max_length=50, unique=True, verbose_name='Kod'),
        ),
        migrations.AlterField(
            model_name='olympiadprogramcode',
            name='icon_class',
            field=models.CharField(default='fas fa-medal', max_length=80, verbose_name='Ikonka'),
        ),
        migrations.AlterField(
            model_name='olympiadprogramcode',
            name='order',
            field=models.PositiveIntegerField(default=1, verbose_name='Tartib raqami'),
        ),
        migrations.RunPython(seed_builtin_codes, unseed_builtin_codes),
    ]
