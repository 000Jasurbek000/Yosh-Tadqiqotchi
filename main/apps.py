from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import main.signals  # noqa: F401
        self._apply_runtime_overrides()
        from django.db.backends.signals import connection_created
        from django.dispatch import receiver

        @receiver(connection_created, dispatch_uid='sqlite_wal_pragmas')
        def _sqlite_wal(sender, connection, **kwargs):
            if connection.vendor == 'sqlite':
                cursor = connection.cursor()
                cursor.execute('PRAGMA journal_mode=WAL;')
                cursor.execute('PRAGMA synchronous=NORMAL;')
                cursor.execute('PRAGMA busy_timeout=20000;')
                cursor.execute('PRAGMA cache_size=-20000;')
                cursor.execute('PRAGMA temp_store=MEMORY;')

    @staticmethod
    def _apply_runtime_overrides():
        """Server settings.py ni almashtirmasdan kerakli sozlamalar."""
        from django.conf import settings

        settings.AUTH_PASSWORD_VALIDATORS = [
            {
                'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
                'OPTIONS': {'min_length': 5},
            },
        ]
        settings.EMAIL_BACKEND = 'main.email_backend.IPv4EmailBackend'
        if not getattr(settings, 'EMAIL_TIMEOUT', None):
            settings.EMAIL_TIMEOUT = 8
        if not getattr(settings, 'SUPERVISOR_NOTIFY_EMAIL', ''):
            settings.SUPERVISOR_NOTIFY_EMAIL = 'jdavletov143@gmail.com'
        settings.AUTHENTICATION_BACKENDS = [
            'main.backends.EmailBackend',
            'django.contrib.auth.backends.ModelBackend',
        ]
        mw = list(settings.MIDDLEWARE)
        if 'main.language.LanguageMiddleware' not in mw:
            insert_at = 0
            for i, item in enumerate(mw):
                if 'SessionMiddleware' in item:
                    insert_at = i + 1
                    break
            mw.insert(insert_at, 'main.language.LanguageMiddleware')
            settings.MIDDLEWARE = mw
        for engine in settings.TEMPLATES:
            cps = engine.get('OPTIONS', {}).get('context_processors', [])
            if 'main.language.language_context' not in cps:
                cps.append('main.language.language_context')
                engine['OPTIONS']['context_processors'] = cps
