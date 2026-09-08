"""Chatbot orchestration: retrieve → context → RapidAPI."""
from main.chat_api import call_chat_api
from .prompts import PLATFORM_SYSTEM_PROMPT, NO_CONTEXT_REPLY, SECURITY_REFUSAL
from .retrieve import retrieve, build_user_message_with_context, is_security_query


def answer_question(user_message: str, history=None):
    """
    Returns: (reply_text, meta_dict)
    meta: {used_rag, chunk_count, max_score, sources}
    """
    history = history or []
    meta = {'used_rag': True, 'chunk_count': 0, 'max_score': 0.0, 'sources': []}

    if is_security_query(user_message):
        return SECURITY_REFUSAL, {**meta, 'used_rag': False, 'security': True}

    chunks, max_score, context_text = retrieve(user_message)
    meta['chunk_count'] = len(chunks)
    meta['max_score'] = max_score
    meta['sources'] = [
        {'title': c['title'], 'url': c['url'], 'score': round(c['score'], 3)}
        for c in chunks[:5]
    ]

    # Hech narsa topilmasa — GPT'ga umumiy bilim bermaslik
    if not chunks:
        return NO_CONTEXT_REPLY, meta

    messages_list = []
    for h in history[-8:]:
        role = h.get('role')
        content = (h.get('content') or '').strip()
        if role in ('user', 'assistant') and content:
            # Tarixdagi assistant javoblarini saqlaymiz, lekin faktlar uchun context yangi
            messages_list.append({'role': role, 'content': content[:800]})

    messages_list.append({
        'role': 'user',
        'content': build_user_message_with_context(user_message, context_text),
    })

    reply, error = call_chat_api(messages_list, PLATFORM_SYSTEM_PROMPT)
    if error:
        return error, {**meta, 'error': True}
    return reply, meta
