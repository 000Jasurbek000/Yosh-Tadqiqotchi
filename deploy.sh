#!/usr/bin/env bash
# ============================================================
# Yosh Tadqiqotchi — server deploy
# Ishlatish:  bash deploy.sh
#
# Serverdagi BULAR o'zgarmaydi / ustiga yozilmaydi:
#   - xalikova_project/settings.py
#   - requirements.txt
#   - .env
#   - db.sqlite3 (va -wal/-shm)
#   - media/
#
# pip install ishlatilmaydi (virtualenv serverdagidek qoladi).
# git reset --hard / stash pop YO'Q.
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

KEEP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/yt-keep.XXXXXX")"
cleanup() { rm -rf "$KEEP_DIR"; }
trap cleanup EXIT

keep_file() {
  local rel="$1"
  if [[ -f "$APP_DIR/$rel" ]]; then
    mkdir -p "$KEEP_DIR/$(dirname "$rel")"
    cp -a "$APP_DIR/$rel" "$KEEP_DIR/$rel"
    echo "==> Saqlandi (server): $rel"
  fi
}

restore_file() {
  local rel="$1"
  if [[ -f "$KEEP_DIR/$rel" ]]; then
    mkdir -p "$APP_DIR/$(dirname "$rel")"
    cp -a "$KEEP_DIR/$rel" "$APP_DIR/$rel"
    echo "==> Qaytarildi (server): $rel"
  fi
}

keep_file "xalikova_project/settings.py"
keep_file "requirements.txt"
keep_file ".env"

echo "==> git fetch / pull (settings/requirements tegilmaydi)..."
git fetch "$REMOTE" "$BRANCH"

git update-index --skip-worktree "xalikova_project/settings.py" 2>/dev/null || true
git update-index --skip-worktree "requirements.txt" 2>/dev/null || true

if ! git pull --ff-only "$REMOTE" "$BRANCH"; then
  echo "OGOHLANTIRISH: pull to'xtadi, server sozlamalarini saqlab qayta uriniladi."
  git checkout -- "xalikova_project/settings.py" "requirements.txt" 2>/dev/null || true
  git pull --ff-only "$REMOTE" "$BRANCH"
fi

restore_file "xalikova_project/settings.py"
restore_file "requirements.txt"
restore_file ".env"

git update-index --skip-worktree "xalikova_project/settings.py" 2>/dev/null || true
git update-index --skip-worktree "requirements.txt" 2>/dev/null || true

if [[ -n "${CONDA_PREFIX:-}" ]] || [[ -n "${VIRTUAL_ENV:-}" ]]; then
  PYTHON=python
  echo "==> Faol muhit: ${CONDA_DEFAULT_ENV:-${VIRTUAL_ENV:-conda/venv}}"
elif [[ -z "$VENV_DIR" ]]; then
  if [[ -d "$APP_DIR/.venv" ]]; then
    VENV_DIR="$APP_DIR/.venv"
  elif [[ -d "$APP_DIR/venv" ]]; then
    VENV_DIR="$APP_DIR/venv"
  fi
fi

if [[ -z "${PYTHON:-}" ]]; then
  if [[ -n "${VENV_DIR:-}" && -f "$VENV_DIR/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    PYTHON=python
  else
    PYTHON="${DEPLOY_PYTHON:-python3}"
  fi
fi

echo "==> pip o'tkazib yuborildi (requirements serverdagidek)"

echo "==> migrate (faqat yangi ustunlar; db.sqlite3 o'chirilmaydi)"
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
echo "OK — kod yangilandi."
echo "O'zgarmagan: settings.py, requirements.txt, .env, db.sqlite3, media/"
