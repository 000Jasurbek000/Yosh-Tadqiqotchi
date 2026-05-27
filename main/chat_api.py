"""Tadqiqotchi AI chatbot — tashqi API chaqiruvlari."""
import logging
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_CHAT_URL = 'https://chatgpt-42.p.rapidapi.com/conversationgpt4-2'
DEFAULT_CHAT_HOST = 'chatgpt-42.p.rapidapi.com'


def _extract_reply(resp_data):
    if not isinstance(resp_data, dict):
        return None
    if resp_data.get('result'):
        return str(resp_data['result']).strip()
    if resp_data.get('message'):
        return str(resp_data['message']).strip()
    choices = resp_data.get('choices') or []
    if choices:
        msg = choices[0].get('message', {}).get('content')
        if msg:
            return str(msg).strip()
    return None


def call_chat_api(messages_list, system_prompt):
    """
    RapidAPI orqali chat javobini olish.
    Server bloklashi yoki vaqtinchalik xatolarda qayta urinadi.
    """
    api_key = (getattr(settings, 'RAPIDAPI_KEY', '') or '').strip()
    if not api_key:
        return None, (
            'Chatbot hozir faol emas. Administrator RAPIDAPI_KEY ni .env faylida sozlasin.'
        )

    url = getattr(settings, 'CHAT_API_URL', DEFAULT_CHAT_URL)
    host = getattr(settings, 'CHAT_API_HOST', DEFAULT_CHAT_HOST)
    timeout = int(getattr(settings, 'CHAT_API_TIMEOUT', 30))
    retries = int(getattr(settings, 'CHAT_API_RETRIES', 2))

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'User-Agent': 'YoshTadqiqotchi/1.0 Django',
        'x-rapidapi-host': host,
        'x-rapidapi-key': api_key,
    }

    payload = {
        'messages': messages_list,
        'system_prompt': system_prompt,
        'temperature': 0.3,
        'top_k': 5,
        'top_p': 0.9,
        'max_tokens': 400,
        'web_access': True,
    }

    last_error = 'Javob olishda xatolik yuz berdi.'

    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout)

            if resp.status_code == 401:
                return None, 'API kalit noto\'g\'ri. Administratorga murojaat qiling.'
            if resp.status_code == 403:
                return None, 'API kirish rad etildi. Kalit yoki obunani tekshiring.'
            if resp.status_code == 429:
                last_error = 'API vaqtincha band. Birozdan keyin qayta urinib ko\'ring.'
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                return None, last_error
            if resp.status_code >= 500:
                last_error = 'Tashqi server vaqtincha ishlamayapti.'
                if attempt < retries:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                return None, last_error

            resp.raise_for_status()

            try:
                resp_data = resp.json()
            except ValueError:
                last_error = 'API noto\'g\'ri javob qaytardi.'
                continue

            reply = _extract_reply(resp_data)
            if reply:
                return reply, None

            last_error = 'Bo\'sh javob qaytdi. Qayta urinib ko\'ring.'

        except requests.Timeout:
            last_error = 'Server javob bermadi. Qayta urinib ko\'ring.'
            if attempt < retries:
                time.sleep(1.0)
                continue
        except requests.ConnectionError:
            last_error = 'Internet yoki tashqi serverga ulanib bo\'lmadi.'
            if attempt < retries:
                time.sleep(1.5)
                continue
        except requests.RequestException as exc:
            logger.warning('Chat API xatolik: %s', exc)
            last_error = 'Tarmoq xatoligi. Keyinroq qayta urinib ko\'ring.'
            if attempt < retries:
                time.sleep(1.0)
                continue

    return None, last_error
