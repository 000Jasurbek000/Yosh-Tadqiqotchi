from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Qaysi baza ishlatilayotganini va yaqin atrofdagi sqlite fayllarni ko'rsatadi."

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        name = Path(str(db.get('NAME', '')))
        self.stdout.write(f"ENGINE: {db.get('ENGINE')}")
        self.stdout.write(f"NAME:   {name}")
        self.stdout.write(f"Bor:    {name.exists()}")
        if name.exists():
            self.stdout.write(f"Hajm:   {name.stat().st_size} bayt")

        try:
            from main.models import User, Announcement, Course
            self.stdout.write(f"User:         {User.objects.count()}")
            self.stdout.write(f"E'lon:        {Announcement.objects.count()}")
            self.stdout.write(f"Kurs:         {Course.objects.count()}")
            staff = list(
                User.objects.filter(is_staff=True).values_list('username', 'email')[:10]
            )
            self.stdout.write(f"Xodimlar:     {staff}")
        except Exception as exc:
            self.stdout.write(f"Jadval o'qilmadi: {exc}")

        roots = [
            Path(settings.BASE_DIR),
            Path(settings.BASE_DIR) / 'db_backups',
            Path(settings.BASE_DIR).parent,
        ]
        self.stdout.write('\nYaqin atrofdagi sqlite fayllar:')
        seen = set()
        for root in roots:
            if not root.exists():
                continue
            for pattern in ('db.sqlite3', '*.sqlite3', '*.db'):
                for path in root.glob(pattern):
                    key = str(path.resolve()) if path.exists() else str(path)
                    if key in seen or not path.is_file():
                        continue
                    seen.add(key)
                    self.stdout.write(f"  {path.stat().st_size:12}  {path}")
