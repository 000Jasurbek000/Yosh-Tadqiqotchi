#!/usr/bin/env bash
# ============================================================
# Yosh Tadqiqotchi — server deploy
# Ishlatish (loyihaning root papkasida):
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Nima QILMAYDI:
#   - git commit / push
#   - .env ni o'zgartirish yoki ustiga yozish
#   - settings.py ni qo'lda o'zgartirish
#   - media / db ni o'chirish
#   - makemigrations (faqat migrate)
#
# Nima QILADI:
#   - git pull
#   - pip dependencies (agar requirements.txt bo'lsa)
#   - migrate
#   - knowledge index
#   - collectstatic
#   - web-xizmatni restart
# ============================================================

set -euo pipefail

# --- Sozlamalar (serverga moslab o'zgartiring) ---
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="${DEPLOY_BRANCH:-main}"
REMOTE="${DEPLOY_REMOTE:-origin}"
# Virtualenv yo'li (bo'sh qoldirilsa: .venv yoki venv avtomatik topiladi)
VENV_DIR="${DEPLOY_VENV:-}"
# systemd service nomi (bo'sh bo'lsa — restart o'tkazib yuboriladi)
SERVICE_NAME="${DEPLOY_SERVICE:-}"
# Masalan: gunicorn, xalikova, yoshtadqiqotchi
# Knowledge indeks (birinchi marta yoki to'liq qayta: DEPLOY_FULL_INDEX=1 ./deploy.sh)
FULL_INDEX="${DEPLOY_FULL_INDEX:-0}"

cd "$APP_DIR"

echo "==> Loyiha: $APP_DIR"
echo "==> Branch: $REMOTE/$BRANCH"

# --- .env ni himoya qilish (hech qachon gitdan kelmasin) ---
ENV_FILE="$APP_DIR/.env"
ENV_BACKUP=""
if [[ -f "$ENV_FILE" ]]; then
  ENV_BACKUP="$(mktemp)"
  cp -a "$ENV_FILE" "$ENV_BACKUP"
  echo "==> .env saqlandi (backup)"
fi

# --- Git pull (commit qilmaydi, faqat yangilaydi) ---
echo "==> git fetch / pull..."
git fetch "$REMOTE" "$BRANCH"

# Lokal commitlanmagan o'zgarishlar bo'lsa — ogohlantirib to'xtatamiz
# (.env gitignore'da, lekin boshqa fayllar bo'lishi mumkin)
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "XATO: Serverda commitlanmagan o'zgarishlar bor."
  echo "Ular deploy paytida aralashib ketishi mumkin."
  echo "Tekshiring: git status"
  echo "Agar faqat vaqtinchalik fayl bo'lsa: git stash -u  (yoki qo'lda tozalang)"
  exit 1
fi

git pull --ff-only "$REMOTE" "$BRANCH"

# .env ni qayta tiklash (agar biror sabab bilan o'zgargan bo'lsa)
if [[ -n "$ENV_BACKUP" && -f "$ENV_BACKUP" ]]; then
  if [[ ! -f "$ENV_FILE" ]] || ! cmp -s "$ENV_BACKUP" "$ENV_FILE"; then
    echo "==> .env tiklanmoqda (serverdagi asl nusxa saqlanadi)"
    cp -a "$ENV_BACKUP" "$ENV_FILE"
  fi
  rm -f "$ENV_BACKUP"
  echo "==> .env saqlab qolindi (o'zgartirilmadi)"
fi

# settings.py ga qo'lda tegmaymiz — faqat gitdagi kod keladi;
# maxfiy/sozlama qiymatlar .env orqali o'qiladi.

# --- Virtualenv ---
if [[ -z "$VENV_DIR" ]]; then
  if [[ -d "$APP_DIR/.venv" ]]; then
    VENV_DIR="$APP_DIR/.venv"
  elif [[ -d "$APP_DIR/venv" ]]; then
    VENV_DIR="$APP_DIR/venv"
  fi
fi

if [[ -n "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  echo "==> venv: $VENV_DIR"
  PYTHON=python
  PIP=pip
elif [[ -n "$VENV_DIR" && -f "$VENV_DIR/Scripts/activate" ]]; then
  # Windows-style (kamdan-kam serverda)
  # shellcheck source=/dev/null
  source "$VENV_DIR/Scripts/activate"
  PYTHON=python
  PIP=pip
else
  PYTHON="${DEPLOY_PYTHON:-python3}"
  PIP="${DEPLOY_PIP:-pip3}"
  echo "==> venv topilmadi, ishlatiladi: $PYTHON"
fi

# --- Dependencies ---
if [[ -f "$APP_DIR/requirements.txt" ]]; then
  echo "==> pip install -r requirements.txt"
  "$PIP" install -r "$APP_DIR/requirements.txt" -q
fi

# --- Django ---
echo "==> migrate"
"$PYTHON" manage.py migrate --noinput

echo "==> knowledge index"
if [[ "$FULL_INDEX" == "1" ]]; then
  "$PYTHON" manage.py index_knowledge --full
else
  "$PYTHON" manage.py index_knowledge
fi

echo "==> collectstatic"
"$PYTHON" manage.py collectstatic --noinput

echo "==> Django check"
"$PYTHON" manage.py check

# --- Restart ---
if [[ -n "$SERVICE_NAME" ]]; then
  echo "==> systemctl restart $SERVICE_NAME"
  if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl restart "$SERVICE_NAME"
    sudo systemctl --no-pager --full status "$SERVICE_NAME" | head -n 20 || true
  else
    echo "OGOHLANTIRISH: systemctl yo'q — xizmatni qo'lda restart qiling."
  fi
else
  echo "==> Restart o'tkazib yuborildi."
  echo "    Bir marta sozlang, masalan:"
  echo "      export DEPLOY_SERVICE=gunicorn"
  echo "    yoki deploy.sh ichida SERVICE_NAME ni yozing."
  echo "    Keyin: sudo systemctl restart <service>"
fi

echo ""
echo "OK — deploy tugadi."
echo "Eslatma: .env va server sozlamalari o'zgartirilmadi."
