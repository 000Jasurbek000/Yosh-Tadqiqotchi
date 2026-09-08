from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
import logging

from .models import (
    Course, Module,
    StateScholarship, BuxduScholarship, BuxduWinnerDatabase,
    Olympiad, BuxduOlympiad, Conference, ResearcherRegulation,
    Literature, Announcement, OakDatabase,
    DissertationBank, ArticleBank, TalentedStudentDatabase,
    ScientificSupervisor, OlympiadProgram, AssessmentTest, Survey,
)

logger = logging.getLogger(__name__)

# Chatbot knowledge — saqlanganda / o'chirilganda avtomatik indeks
KNOWLEDGE_MODELS = (
    StateScholarship, BuxduScholarship, BuxduWinnerDatabase,
    Olympiad, BuxduOlympiad, OlympiadProgram, Conference,
    ResearcherRegulation, Literature, Course, Announcement,
    OakDatabase, DissertationBank, ArticleBank,
    TalentedStudentDatabase, ScientificSupervisor,
    AssessmentTest, Survey,
)


@receiver(post_save, sender=Course)
def create_course_modules(sender, instance, created, **kwargs):
    """
    Course yaratilganda yoki module_count o'zgarganda
    avtomatik modullar yaratadi yoki yangilaydi
    """
    if created or instance.module_count:
        current_modules = instance.modules.count()
        target_count = instance.module_count

        if current_modules < target_count:
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
            instance.modules.filter(number__gt=target_count).delete()


def _safe_index(instance):
    try:
        from main.knowledge.ingest import index_instance
        index_instance(instance)
    except Exception:
        logger.exception(
            'Knowledge index yangilanmadi: %s pk=%s',
            type(instance).__name__,
            getattr(instance, 'pk', None),
        )


def _safe_delete_chunks(instance):
    try:
        from main.knowledge.ingest import delete_instance_chunks
        delete_instance_chunks(instance)
    except Exception:
        logger.exception('Knowledge chunk o\'chirilmadi: %s', type(instance).__name__)


def _on_knowledge_save(sender, instance, **kwargs):
    transaction.on_commit(lambda obj=instance: _safe_index(obj))


def _on_knowledge_delete(sender, instance, **kwargs):
    pk = instance.pk
    cls = instance.__class__

    def _run():
        stub = cls(pk=pk)
        _safe_delete_chunks(stub)

    transaction.on_commit(_run)


for _model in KNOWLEDGE_MODELS:
    post_save.connect(_on_knowledge_save, sender=_model, dispatch_uid=f'kb_save_{_model.__name__}')
    post_delete.connect(_on_knowledge_delete, sender=_model, dispatch_uid=f'kb_del_{_model.__name__}')
