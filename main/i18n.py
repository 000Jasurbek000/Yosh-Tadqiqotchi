import json
import threading
from pathlib import Path

SUPPORTED_LANGS = ('uz', 'ru', 'en')
DEFAULT_LANG = 'uz'

_cache = {}
_local = threading.local()
_LOCALE_DIR = Path(__file__).resolve().parent.parent / 'locale'


class AttrDict:
    def __init__(self, data, fallback=None):
        self._data = data or {}
        self._fallback = fallback or {}

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        val = self._data.get(name)
        if val is None:
            val = self._fallback.get(name, name)
        if isinstance(val, dict):
            fb = self._fallback.get(name) if isinstance(self._fallback.get(name), dict) else {}
            return AttrDict(val, fb)
        return val

    def __getitem__(self, name):
        return getattr(self, name)


def load_catalog(lang):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    if lang in _cache:
        return _cache[lang]
    path = _LOCALE_DIR / f'{lang}.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        data = {}
    _cache[lang] = data
    return data


def set_current_language(lang):
    _local.lang = lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def get_current_language():
    return getattr(_local, 'lang', DEFAULT_LANG)


def _lookup(data, key):
    cur = data
    for part in key.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur if not isinstance(cur, dict) else None


def t(key, **kwargs):
    lang = get_current_language()
    value = _lookup(load_catalog(lang), key)
    if value is None and lang != DEFAULT_LANG:
        value = _lookup(load_catalog(DEFAULT_LANG), key)
    if value is None:
        value = key
    if kwargs:
        try:
            value = value.format(**kwargs)
        except Exception:
            pass
    return value


def translations_for(lang=None):
    lang = lang or get_current_language()
    data = load_catalog(lang)
    fallback = load_catalog(DEFAULT_LANG) if lang != DEFAULT_LANG else {}
    return AttrDict(data, fallback)


def user_test_target(user):
    degree = (getattr(user, 'academic_degree', '') or '').strip()
    if degree == 'magistr':
        return 'magistr'
    if degree == 'bakalavr':
        stage = (getattr(user, 'education_stage', '') or '').strip()
        if stage in ('1-kurs', '2-kurs', '3-kurs', '4-kurs'):
            return stage
    return None
