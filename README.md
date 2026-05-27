# Yosh Tadqiqotchi

Buxoro davlat universiteti iqtidorli talabalar uchun ilmiy-tadqiqot platformasi (Django).

## Tez boshlash (local)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/Mac
```

`.env` faylini ochib, quyidagilarni to'ldiring:

- `SECRET_KEY` — yangi random kalit
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` — Gmail App Password
- `RAPIDAPI_KEY` — chatbot uchun RapidAPI kaliti

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/  
Admin: http://127.0.0.1:8000/admin/

## GitHubga yuklash

Maxfiy ma'lumotlar **kodda emas**, faqat `.env` faylida saqlanadi. `.env` `.gitignore` da — GitHubga ketmaydi.

```bash
git add .
git commit -m "Yosh Tadqiqotchi — to'liq platforma"
git push origin main
```

Repository: https://github.com/000Jasurbek000/Yosh-Tadqiqotchi

## Production server (Render / Railway / VPS)

1. Repositoryni ulang
2. Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
3. Start: `gunicorn xalikova_project.wsgi:application --bind 0.0.0.0:$PORT`  
   (yoki `Procfile` dan foydalaning)

### Environment variables (server panelida)

| O'zgaruvchi | Tavsif |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | Kuchli random kalit |
| `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.com` |
| `RAPIDAPI_KEY` | RapidAPI kaliti |
| `EMAIL_HOST_USER` | Gmail |
| `EMAIL_HOST_PASSWORD` | Gmail App Password |
| `DEFAULT_FROM_EMAIL` | Yuboruvchi email |
| `ADMIN_EMAIL` | Admin email |
| `SERVE_MEDIA` | `True` (yuklangan fayllar uchun) |

### Chatbot API (tashqi server bloklamasligi uchun)

- Kalit `.env` / server environment da bo'lishi shart
- `CHAT_API_TIMEOUT=30` va `CHAT_API_RETRIES=2` — sekin serverlarda yordam beradi
- Agar hosting outbound HTTP ni bloklasa, VPS yoki Render/Railway kabi platformani tanlang
- RapidAPI obunasini tekshiring (429 xato = limit tugagan)

## PostgreSQL (ixtiyoriy)

SQLite o'rniga PostgreSQL:

```env
DB_ENGINE=postgresql
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
```

## Loyiha tuzilmasi

- `main/` — asosiy Django app (modellar, viewlar, admin)
- `django_templates/` — HTML shablonlar
- `static/` — CSS, JS, rasmlar
- `media/` — yuklangan fayllar (GitHubga kirmaydi)
- `xalikova_project/` — settings, urls

## Muhim eslatmalar

- `db.sqlite3` va `media/` GitHubga yuklanmaydi
- Gmail parolini oddiy parol emas, **App Password** qiling
- Productionda `DEBUG=False` qo'ying
