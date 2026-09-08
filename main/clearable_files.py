"""
Admin: fayl maydonlarida 'Eski faylni o'chirish' checkboxi (o'zbekcha).
Yangi fayl yuklanganda eski fayl diskdan ham o'chiriladi.
"""
from django import forms
from django.db import models


class UzbekClearableFileInput(forms.ClearableFileInput):
    initial_text = 'Hozirgi fayl'
    input_text = 'Yangi fayl tanlash'
    clear_checkbox_label = "Eski faylni o'chirish"


def _delete_storage_file(file_field):
    if not file_field:
        return
    try:
        name = getattr(file_field, 'name', None)
        if name and file_field.storage.exists(name):
            file_field.storage.delete(name)
    except Exception:
        pass


class ClearableFileAdminMixin:
    """
    clearable_file_fields — ixtiyoriy (hujjat uchun).
    Asosiy: FileField/ImageField widgetlari o'zbekcha clear checkbox bilan.
    """
    clearable_file_fields = ()

    formfield_overrides = {
        models.FileField: {'widget': UzbekClearableFileInput},
        models.ImageField: {'widget': UzbekClearableFileInput},
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, (models.FileField, models.ImageField)):
            kwargs.setdefault('widget', UzbekClearableFileInput)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Yangi fayl yuklanganda eski faylni diskdan o'chirish."""
        if change and obj.pk:
            try:
                old = type(obj).objects.get(pk=obj.pk)
            except type(obj).DoesNotExist:
                old = None
            if old:
                for field in obj._meta.fields:
                    if not isinstance(field, (models.FileField, models.ImageField)):
                        continue
                    old_file = getattr(old, field.name, None)
                    new_file = getattr(obj, field.name, None)
                    old_name = getattr(old_file, 'name', None) or ''
                    new_name = getattr(new_file, 'name', None) or ''
                    # Cleared yoki almashtirilgan
                    if old_name and old_name != new_name:
                        _delete_storage_file(old_file)
        super().save_model(request, obj, form, change)
