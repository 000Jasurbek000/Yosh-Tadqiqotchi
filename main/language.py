from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .i18n import (
    SUPPORTED_LANGS, DEFAULT_LANG, set_current_language,
    get_current_language, translations_for,
)


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = (
            request.GET.get('lang')
            or request.session.get('site_lang')
            or request.COOKIES.get('site_lang')
            or DEFAULT_LANG
        )
        if lang not in SUPPORTED_LANGS:
            lang = DEFAULT_LANG
        request.LANGUAGE_CODE = lang
        request.session['site_lang'] = lang
        set_current_language(lang)
        response = self.get_response(request)
        response.set_cookie('site_lang', lang, max_age=60 * 60 * 24 * 365, samesite='Lax')
        return response


def language_context(request):
    lang = getattr(request, 'LANGUAGE_CODE', get_current_language())
    return {
        'lang': lang,
        'tr': translations_for(lang),
        'available_langs': [
            {'code': 'uz', 'flag': '🇺🇿', 'name': 'Oʻzbekcha'},
            {'code': 'ru', 'flag': '🇷🇺', 'name': 'Русский'},
            {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
        ],
    }


@require_POST
def set_language(request):
    lang = request.POST.get('language', DEFAULT_LANG)
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    request.session['site_lang'] = lang
    nxt = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    response = redirect(nxt)
    response.set_cookie('site_lang', lang, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response
