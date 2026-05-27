"""Ko'rsatish uchun yordamchi funksiyalar."""

ASSESSMENT_STATUS_LABELS = {
    'oddiy': 'Oddiy',
    'iqtidorli': 'Iqtidorli',
}


def format_assessment_status(user):
    """User.assessment_status uchun o'qiladigan matn (choices yo'q)."""
    if not user or not getattr(user, 'assessment_status', None):
        return '—'
    return ASSESSMENT_STATUS_LABELS.get(user.assessment_status, user.assessment_status)
