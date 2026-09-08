"""Oddiy tokenlash va sinonimlar — embedding API'siz semantic-ish retrieval."""
import re
import hashlib

STOPWORDS = {
    'va', 'yoki', 'uchun', 'bilan', 'ham', 'bu', 'shu', 'men', 'biz', 'siz',
    'qanday', 'qaysi', 'nima', 'qayerda', 'qachon', 'nega', 'nimaga',
    'bor', 'yoq', "yo'q", 'haqida', 'mumkin', 'kerak', 'deb', 'degan',
    'ga', 'ni', 'da', 'dan', 'ning', 'lar', 'lari', 'the', 'a', 'an', 'is',
    'how', 'what', 'where', 'can', 'i', 'to', 'of', 'in', 'on', 'for',
    'olish', 'qilish', 'bolish', "bo'lish", 'ber', 'ayt', 'sanab',
}

SYNONYMS = {
    'stipendiya': ['stipendiya', 'stipendiyalar', 'grant', 'grantlar', 'moliyaviy', 'scholarship'],
    'olimpiada': ['olimpiada', 'olimpiadalar', 'tanlov', 'tanlovlar', 'musobaqa', 'olympiad'],
    'iqtidorli': ['iqtidorli', 'iqtidor', 'iqtidorli talaba', 'saralash', 'talented'],
    'kurs': ['kurs', 'kurslar', 'modul', 'modullar', "o'quv", 'course'],
    'konferensiya': ['konferensiya', 'konferensiyalar', 'conference'],
    'nizom': ['nizom', 'nizomlar', 'qoida', 'tartib', 'regulation'],
    'adabiyot': ['adabiyot', 'adabiyotlar', 'kitob', 'literature'],
    'rahbar': ['rahbar', 'ilmiy rahbar', 'supervisor', 'professor'],
    'ariza': ['ariza', 'topshirish', "ro'yxatdan", 'registratsiya', 'application'],
    'sertifikat': ['sertifikat', 'certificate', 'diplom'],
    'jurnal': ['jurnal', 'jurnallar', 'maqola', 'oak', 'journal'],
    'buxdu': ['buxdu', 'buxoro', 'buxoro davlat'],
    'davlat': ['davlat', 'respublika', 'fitrat', 'state'],
}


def normalize_text(text: str) -> str:
    if not text:
        return ''
    text = text.lower().replace('ʻ', "'").replace('ʼ', "'").replace('`', "'")
    text = re.sub(r'[^\w\s\'\-]', ' ', text, flags=re.UNICODE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text: str, expand_synonyms: bool = True) -> list:
    text = normalize_text(text)
    tokens = [t for t in text.split() if len(t) > 1 and t not in STOPWORDS]
    if not expand_synonyms:
        return tokens
    expanded = list(tokens)
    joined = ' ' + ' '.join(tokens) + ' '
    for canonical, variants in SYNONYMS.items():
        for v in variants:
            if v in joined or any(v == t or (len(v) > 3 and v in t) for t in tokens):
                expanded.append(canonical)
                expanded.extend(variants)
                break
    return expanded


def content_hash(title: str, content: str, source_type: str, object_id: str = '') -> str:
    raw = f'{source_type}|{object_id}|{title}|{content}'
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def score_overlap(query_tokens: list, doc_tokens: list, priority: int = 50) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    q_set = set(query_tokens)
    d_set = set(doc_tokens)
    inter = q_set & d_set
    if not inter:
        return 0.0
    coverage = len(inter) / max(len(q_set), 1)
    jaccard = len(inter) / max(len(q_set | d_set), 1)
    priority_boost = priority / 100.0
    return (0.55 * coverage) + (0.30 * jaccard) + (0.15 * priority_boost)
