#!/usr/bin/env bash
# ============================================================
# Yosh Tadqiqotchi — server deploy
# Ishlatish:  bash deploy.sh
#
# Nima QILMAYDI:
#   - git commit / push
#   - .env ni o'zgartirish
#   - db.sqlite3 / media ni o'chirish
#   - git reset --hard / stash pop
#   - makemigrations
# ============================================================

set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="${DEPLOY_BRANCH:-main}"
REMOTE="${DEPLOY_REMOTE:-origin}"
VENV_DIR="${DEPLOY_VENV:-}"
SERVICE_NAME="${DEPLOY_SERVICE:-}"
FULL_INDEX="${DEPLOY_FULL_INDEX:-0}"

cd "$APP_DIR"

echo "==> Loyiha: $APP_DIR"
echo "==> Branch: $REMOTE/$BRANCH"

ENV_FILE="$APP_DIR/.env"
ENV_BACKUP=""
if [[ -f "$ENV_FILE" ]]; then
  ENV_BACKUP="$(mktemp)"
  cp -a "$ENV_FILE" "$ENV_BACKUP"
  echo "==> .env saqlandi"
fi

echo "==> git fetch / pull..."
git fetch "$REMOTE" "$BRANCH"
if ! git pull --ff-only "$REMOTE" "$BRANCH"; then
  echo "XATO: git pull muvaffaqiyatsiz."
  echo "Serverda lokal o'zgarish bo'lsa, settings.py ni tahrirlamang — .env ishlating."
  exit 1
fi

if [[ -n "$ENV_BACKUP" && -f "$ENV_BACKUP" ]]; then
  cp -a "$ENV_BACKUP" "$ENV_FILE"
  rm -f "$ENV_BACKUP"
  echo "==> .env tiklandi (o'zgartirilmadi)"
fi

if [[ -n "${CONDA_PREFIX:-}" ]] || [[ -n "${VIRTUAL_ENV:-}" ]]; then
  PYTHON=python
  PIP=pip
  echo "==> Faol muhit: ${CONDA_DEFAULT_ENV:-${VIRTUAL_ENV:-conda/venv}}"
elif [[ -z "$VENV_DIR" ]]; then
  if [[ -d "$APP_DIR/.venv" ]]; then
    VENV_DIR="$APP_DIR/.venv"
  elif [[ -d "$APP_DIR/venv" ]]; then
    VENV_DIR="$APP_DIR/venv"
  fi
fi

if [[ -z "${PYTHON:-}" ]]; then
  if [[ -n "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    PYTHON=python
    PIP=pip
  else
    PYTHON="${DEPLOY_PYTHON:-python3}"
    PIP="${DEPLOY_PIP:-pip3}"
  fi
fi

if [[ -f "$APP_DIR/requirements.txt" ]]; then
  echo "==> pip install -r requirements.txt"
  "$PIP" install -r "$APP_DIR/requirements.txt" -q
fi

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

restarted=0
if [[ -f "$APP_DIR/passenger_wsgi.py" ]] || [[ -d "$APP_DIR/tmp" ]] || [[ -d "$APP_DIR/public" ]]; then
  mkdir -p "$APP_DIR/tmp"
  touch "$APP_DIR/tmp/restart.txt"
  echo "==> Passenger restart: tmp/restart.txt"
  restarted=1
fi

if [[ -n "$SERVICE_NAME" ]] && command -v systemctl >/dev/null 2>&1; then
  sudo systemctl restart "$SERVICE_NAME"
  restarted=1
fi

if [[ "$restarted" -eq 0 ]]; then
  echo "==> Restart: touch tmp/restart.txt"
fi

echo ""
echo "OK — deploy tugadi. .env va db.sqlite3 o'zgartirilmadi."
