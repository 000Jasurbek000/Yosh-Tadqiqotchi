from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import main.signals  # noqa: F401
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
