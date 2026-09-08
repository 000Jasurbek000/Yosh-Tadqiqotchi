"""Knowledge base'dan relevant chunklarni qidirish."""
from main.models import KnowledgeChunk
from .text_utils import tokenize, score_overlap, SYNONYMS, STOPWORDS
from .prompts import NO_CONTEXT_REPLY  # noqa: F401 — re-export uchun

DEFAULT_THRESHOLD = 0.22
DEFAULT_TOP_K = 8

_PLATFORM_VOCAB = set(SYNONYMS.keys())
for _variants in SYNONYMS.values():
    _PLATFORM_VOCAB.update(_variants)


def retrieve(query: str, top_k: int = DEFAULT_TOP_K, threshold: float = DEFAULT_THRESHOLD):
    """
    Returns: (chunks_list, max_score, context_text)
    """
    query_tokens = tokenize(query)
    core_tokens = tokenize(query, expand_synonyms=False)
    if not query_tokens:
        return [], 0.0, ''

    # Asl savoldagi bosh harfli so'zlar (Fulbright, NASA) — KB da yo'q bo'lsa rad etamiz
    proper_names = {
        w.lower().strip('.,?!«»:;\"\'')
        for w in (query or '').split()
        if len(w) >= 3 and w[0].isupper() and not w.isupper() or (w.isupper() and len(w) >= 3)
    }
    # "IQ" kabi qisqa ALLCAPS ni o'tkazib yuborish; NASA/Fulbright qoladi
    proper_names = {p for p in proper_names if len(p) >= 3 and p not in STOPWORDS and p not in _PLATFORM_VOCAB}

    candidates = list(
        KnowledgeChunk.objects.filter(is_active=True).only(
            'title', 'content', 'url', 'category', 'priority', 'search_text', 'source_type'
        )
    )

    corpus_tokens = set()
    for chunk in candidates:
        corpus_tokens.update((chunk.search_text or '').split())

    missing_names = [n for n in proper_names if n not in corpus_tokens]
    if missing_names:
        return [], 0.0, ''

    scored = []
    for chunk in candidates:
        doc_tokens = (chunk.search_text or '').split() or tokenize(f'{chunk.title} {chunk.content}')
        doc_set = set(doc_tokens)

        score = score_overlap(query_tokens, doc_tokens, priority=chunk.priority)

        if core_tokens:
            core_hits = sum(1 for t in core_tokens if t in doc_set)
            if core_hits == 0:
                continue
            if core_hits / len(core_tokens) < 0.34:
                score *= 0.4

        if score >= threshold:
            scored.append({
                'title': chunk.title,
                'content': chunk.content,
                'url': chunk.url,
                'category': chunk.category,
                'source_type': chunk.source_type,
                'score': score,
            })

    scored.sort(key=lambda x: (-x['score'],))
    top = scored[:top_k]
    max_score = top[0]['score'] if top else 0.0

    if not top:
        return [], 0.0, ''

    parts = []
    from .prompts import format_source_label
    for i, c in enumerate(top, 1):
        src = format_source_label(c.get('url') or '')
        # Contentedagi ichki pathlarni odamona nomga yaqinlashtirish uchun eslatma
        parts.append(
            f"[{i}] {c['title']}\n"
            f"Manba (to'g'ri): {src}\n"
            f"{c['content']}"
        )
    context_text = '\n\n---\n\n'.join(parts)
    return top, max_score, context_text


def build_user_message_with_context(user_question: str, context_text: str) -> str:
    if not context_text:
        return (
            f"RETRIEVED CONTEXT: (bo'sh — platformada mos ma'lumot topilmadi)\n\n"
            f"USER QUESTION: {user_question}\n\n"
            f"Agar context bo'sh bo'lsa, faqat ma'lumot topilmaganini ayting."
        )
    return (
        f"RETRIEVED CONTEXT (Yosh Tadqiqotchi platformasi — yoshtadqiqotchi.uz):\n"
        f"{context_text}\n\n"
        f"USER QUESTION: {user_question}\n\n"
        f"QOIDALAR: Faqat context asosida javob bering. "
        f"Manbada faqat yoshtadqiqotchi.uz domenini ishlating (yosh.tadqiqotchi.uz deb yozmang). "
        f"/assessment-test/ kabi ichki yo'llarni yozmang — sahifa nomini ayting "
        f"(masalan: «Saralash testi» bo'limi)."
    )


def is_security_query(text: str) -> bool:
    from .prompts import SECURITY_PATTERNS
    low = (text or '').lower()
    return any(p in low for p in SECURITY_PATTERNS)
