"""Chatbot orchestration: retrieve → context → RapidAPI."""
import re

from main.chat_api import call_chat_api
from .prompts import (
    PLATFORM_SYSTEM_PROMPT,
    NO_CONTEXT_REPLY,
    SECURITY_REFUSAL,
    SMALLTALK_REPLIES,
    SITE_DOMAIN,
)
from .retrieve import retrieve, build_user_message_with_context, is_security_query


def _normalize_msg(text: str) -> str:
    t = (text or '').strip().lower()
    t = t.replace('ʻ', "'").replace('ʼ', "'").replace('`', "'")
    t = re.sub(r'[?!.,;:]+', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def detect_smalltalk(user_message: str):
    """Salom / qandaysan / sen kimsan — RAG'siz javob. None = smalltalk emas."""
    t = _normalize_msg(user_message)
    if not t or len(t) > 80:
        return None

    who = (
        'sen kimsan', 'kim san', 'kim siz', "o'zing kim", 'ozing kim',
        'who are you', 'what are you', 'isming nima', 'nima deb atalasan',
        'yordamchimisan', 'botmisan', 'ai misan',
    )
    if any(p in t for p in who) or t in ('kim', 'sen kim'):
        return SMALLTALK_REPLIES['who_are_you']

    thanks = ('rahmat', 'tashakkur', 'thanks', 'thank you', 'barakalla')
    if t in thanks or any(t.startswith(p) and len(t) < 25 for p in thanks):
        return SMALLTALK_REPLIES['thanks']

    how = (
        'qandaysan', 'qalaysan', 'qalay', 'yahshimisiz', 'yaxshimisiz',
        'how are you', 'nima gap', 'nima gaplar',
    )
    if t in how or any(p == t or t.startswith(p + ' ') for p in how):
        return SMALLTALK_REPLIES['how_are_you']

    greet = (
        'salom', 'assalomu alaykum', 'assalom', 'hello', 'hi', 'hey',
        'hayrli kun', 'hayrli tong', 'hayrli kech', 'good morning',
    )
    if t in greet or any(t == p or t.startswith(p + ' ') for p in greet):
        # "salom stipendiyalar" kabi aralash savol — smalltalk emas
        words = t.split()
        if len(words) <= 4:
            return SMALLTALK_REPLIES['greeting']

    return None


def sanitize_reply(reply: str) -> str:
    """Noto'g'ri domen va yolg'iz ichki pathlarni tozalash."""
    if not reply:
        return reply
    text = reply
    # Ortiqcha nuqtali / noto'g'ri domen
    text = re.sub(r'https?://yosh\.tadqiqotchi\.uz', f'https://{SITE_DOMAIN}', text, flags=re.I)
    text = re.sub(r'\byosh\.tadqiqotchi\.uz\b', SITE_DOMAIN, text, flags=re.I)
    text = re.sub(r'https?://yoshtadqiqotchi\.z(?=/|\b)', f'https://{SITE_DOMAIN}', text, flags=re.I)

    # Faqat yolg'iz pathlar (to'liq to'g'ri URL ichidagini buzmaslik)
    replacements = [
        (r'/assessment-test/?', "«Saralash testi» bo'limi"),
        (r'/iqtidor-yoli/?', "«Iqtidor Yo'li» bo'limi"),
        (r'/davlat-stipendiyalari/?', '«Davlat stipendiyalari» sahifasi'),
        (r'/buxdu-stipendiyalari/?', '«BuxDU stipendiyalari» sahifasi'),
        (r'/olimpiadalar/?', '«Olimpiadalar» sahifasi'),
        (r'/courses/?', "«Kurslar» bo'limi"),
        (r'/kurslar/?', "«Kurslar» bo'limi"),
        (r'/ilmiy-rahbarlar/?', "«Ilmiy rahbarlar» bo'limi"),
        (r'/ilmiy-nizomlar/?', '«Ilmiy nizomlar» sahifasi'),
        (r'/adabiyotlar/?', '«Adabiyotlar» sahifasi'),
        (r'/register/?', "ro'yxatdan o'tish"),
        (r'/iqtidorli-baza/?', '«Iqtidorli talabalar bazasi»'),
        (r'/platforma-haqida/?', '«Platforma haqida» sahifasi'),
    ]
    for pattern, label in replacements:
        # oldinda domen bo'lmasa — almashtirish
        text = re.sub(
            rf'(?<!{re.escape(SITE_DOMAIN)})(?<!https://)(?<!http://){pattern}',
            label,
            text,
            flags=re.IGNORECASE,
        )

    text = text.replace('assessment_status', 'talaba holati')
    return text


def answer_question(user_message: str, history=None):
    """
    Returns: (reply_text, meta_dict)
    """
    history = history or []
    meta = {'used_rag': True, 'chunk_count': 0, 'max_score': 0.0, 'sources': []}

    if is_security_query(user_message):
        return SECURITY_REFUSAL, {**meta, 'used_rag': False, 'security': True}

    smalltalk = detect_smalltalk(user_message)
    if smalltalk:
        return smalltalk, {**meta, 'used_rag': False, 'smalltalk': True}

    chunks, max_score, context_text = retrieve(user_message)
    meta['chunk_count'] = len(chunks)
    meta['max_score'] = max_score
    meta['sources'] = [
        {'title': c['title'], 'url': c['url'], 'score': round(c['score'], 3)}
        for c in chunks[:5]
    ]

    if not chunks:
        return NO_CONTEXT_REPLY, meta

    messages_list = []
    for h in history[-8:]:
        role = h.get('role')
        content = (h.get('content') or '').strip()
        if role in ('user', 'assistant') and content:
            messages_list.append({'role': role, 'content': content[:800]})

    messages_list.append({
        'role': 'user',
        'content': build_user_message_with_context(user_message, context_text),
    })

    reply, error = call_chat_api(messages_list, PLATFORM_SYSTEM_PROMPT)
    if error:
        return error, {**meta, 'error': True}
    return sanitize_reply(reply), meta
