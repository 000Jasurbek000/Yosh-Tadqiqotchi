import random

from django.db.models import Q

from .i18n import user_test_target, t
from .models import AssessmentTest, Question


def get_assessment_for_user(user):
    qs = AssessmentTest.objects.filter(is_active=True).select_related('test_set')
    target = user_test_target(user)
    if target:
        match = qs.filter(test_set__target_level=target).first()
        if match:
            return match
    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return qs.first()
    if target:
        return qs.filter(Q(test_set__target_level='') | Q(test_set__target_level__isnull=True)).first()
    return None


def assessment_unavailable_message(user):
    degree = (getattr(user, 'academic_degree', '') or '').strip()
    if degree in ('phd', 'dsc'):
        return t('assessment.not_for_degree')
    if degree == 'magistr':
        return t('assessment.no_test_magistr')
    if degree == 'bakalavr':
        return t('assessment.no_test_course', course=getattr(user, 'education_stage', '') or '—')
    return t('assessment.no_test')


def shuffled_questions(request, test_set, prefix, user_id, limit=None):
    questions = list(
        Question.objects.filter(test_set=test_set).prefetch_related('answers')
    )
    if not questions:
        return []

    qkey = f'{prefix}_q_{test_set.id}_{user_id}'
    ids = [q.id for q in questions]
    order = request.session.get(qkey)
    if not order or set(order) != set(ids):
        order = ids[:]
        random.shuffle(order)
        if limit and len(order) > limit:
            order = order[:limit]
        request.session[qkey] = order
        request.session.modified = True
    elif limit:
        order = order[:limit]

    pos = {qid: i for i, qid in enumerate(order)}
    questions = [q for q in questions if q.id in pos]
    questions.sort(key=lambda q: pos.get(q.id, 9999))

    akey = f'{prefix}_a_{test_set.id}_{user_id}'
    ans_map = request.session.get(akey) or {}
    changed = False
    for q in questions:
        aids = [a.id for a in q.answers.all()]
        stored = ans_map.get(str(q.id))
        if not stored or set(stored) != set(aids):
            stored = aids[:]
            random.shuffle(stored)
            ans_map[str(q.id)] = stored
            changed = True
        apos = {aid: i for i, aid in enumerate(stored)}
        q.shuffled_answers = sorted(list(q.answers.all()), key=lambda a: apos.get(a.id, 9999))
    if changed:
        request.session[akey] = ans_map
        request.session.modified = True
    return questions


def clear_test_shuffle(request, test_set, prefix, user_id):
    for suffix in ('q', 'a'):
        key = f'{prefix}_{suffix}_{test_set.id}_{user_id}'
        if key in request.session:
            del request.session[key]
            request.session.modified = True
