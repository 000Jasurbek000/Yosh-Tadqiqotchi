from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        import main.signals
