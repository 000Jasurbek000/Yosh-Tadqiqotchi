from django.shortcuts import redirect

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


def _lang_url(request, code):
    query = request.GET.copy()
    query['lang'] = code
    return f'{request.path}?{query.urlencode()}'


def language_context(request):
    lang = getattr(request, 'LANGUAGE_CODE', get_current_language())
    langs = [
        {'code': 'uz', 'label': 'UZ', 'name': 'Oʻzbekcha'},
        {'code': 'ru', 'label': 'RU', 'name': 'Русский'},
        {'code': 'en', 'label': 'EN', 'name': 'English'},
    ]
    for item in langs:
        item['url'] = _lang_url(request, item['code'])
        item['active'] = item['code'] == lang
    current = next((item for item in langs if item['active']), langs[0])
    return {
        'lang': lang,
        'tr': translations_for(lang),
        'available_langs': langs,
        'current_lang': current,
    }


def set_language(request):
    lang = request.GET.get('lang') or request.POST.get('language', DEFAULT_LANG)
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    request.session['site_lang'] = lang
    nxt = request.POST.get('next') or request.META.get('HTTP_REFERER') or request.GET.get('next') or '/'
    if 'lang=' in nxt:
        nxt = request.path
    response = redirect(nxt)
    response.set_cookie('site_lang', lang, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response
