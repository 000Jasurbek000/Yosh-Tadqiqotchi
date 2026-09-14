from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from .phone_utils import normalize_phone, phone_digits

User = get_user_model()


class PhoneBackend(ModelBackend):
    """Faqat telefon (yoki admin username) orqali kirish."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        user = self._find_user(username)
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def _find_user(self, username):
        raw = (username or '').strip()
        if not raw or '@' in raw:
            return None

        compact = normalize_phone(raw)
        digits = phone_digits(raw)
        qs = User.objects.filter(phone_number__isnull=False).exclude(phone_number='')
        user = qs.filter(phone_number=compact).first()
        if user:
            return user
        if digits:
            for candidate in qs.only('id', 'phone_number').iterator():
                if phone_digits(candidate.phone_number) == digits:
                    return candidate
        try:
            return User.objects.get(username=raw)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# Eski importlar uchun
EmailBackend = PhoneBackend
