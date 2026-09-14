from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Admin akkauntni topadi, is_staff/is_superuser ni yoqadi. Bazani o'chirmaydi."

    def add_arguments(self, parser):
        parser.add_argument('--email', default='umidaxalikova87@mail.ru')
        parser.add_argument('--password', default='', help='Berilsa, parol yangilanadi')

    def handle(self, *args, **options):
        User = get_user_model()
        email = (options.get('email') or '').strip()
        total = User.objects.count()
        staff = list(
            User.objects.filter(is_staff=True).values_list('id', 'username', 'email')
        )
        self.stdout.write(f'Foydalanuvchilar soni: {total}')
        self.stdout.write(f'Xodimlar: {staff}')

        user = (
            User.objects.filter(email__iexact=email).first()
            or User.objects.filter(username__iexact=email).first()
        )
        if user is None:
            self.stderr.write(self.style.ERROR(f'Topilmadi: {email}'))
            return

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        password = options.get('password') or ''
        if password:
            user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f'Tayyor: id={user.pk} username={user.username} email={user.email} '
            f'staff={user.is_staff} super={user.is_superuser}'
        ))
        if not password:
            self.stdout.write(
                f'Parolni almashtirish: python manage.py changepassword {user.username}'
            )
