from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, Module


@receiver(post_save, sender=Course)
def create_course_modules(sender, instance, created, **kwargs):
    """
    Course yaratilganda yoki module_count o'zgarganda
    avtomatik modullar yaratadi yoki yangilaydi
    """
    if created or instance.module_count:
        # Hozirgi modullar sonini tekshirish
        current_modules = instance.modules.count()
        target_count = instance.module_count
        
        if current_modules < target_count:
            # Yetishmayotgan modullarni yaratish
            for i in range(current_modules + 1, target_count + 1):
                Module.objects.get_or_create(
                    course=instance,
                    number=i,
                    defaults={
                        'name': f'Modul {i}',
                        'description': f'{instance.name} - {i}-modul'
                    }
                )
        elif current_modules > target_count:
            # Ortiqcha modullarni o'chirish
            instance.modules.filter(number__gt=target_count).delete()
