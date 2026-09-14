#!/usr/bin/env bash
# ============================================================
# Yosh Tadqiqotchi — server deploy
# Ishlatish:  bash deploy.sh
#
# Serverdagi fayllar HECH QACHON GitHubdagisi bilan almashtirilmaydi:
#   xalikova_project/settings.py
#   requirements.txt
#   .env
#   db.sqlite3 (+ wal/shm)
#   media/
#
# pip install yo'q. git reset --hard yo'q. git stash yo'q.
# git pull ham yo'q (merge/conflict chiqmasin).
# Kod: git fetch + alohida fayllarni origin/main dan olish.
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

KEEP="$(mktemp -d "${TMPDIR:-/tmp}/yt-keep.XXXXXX")"
cleanup() { rm -rf "$KEEP"; }
trap cleanup EXIT

preserve() {
  local rel="$1"
  if [[ -e "$APP_DIR/$rel" ]]; then
    mkdir -p "$KEEP/$(dirname "$rel")"
    cp -a "$APP_DIR/$rel" "$KEEP/$rel"
    echo "==> Saqlandi: $rel"
  fi
}

restore() {
  local rel="$1"
  if [[ -e "$KEEP/$rel" ]]; then
    mkdir -p "$APP_DIR/$(dirname "$rel")"
    cp -a "$KEEP/$rel" "$APP_DIR/$rel"
    echo "==> Qaytarildi: $rel"
  fi
}

preserve "xalikova_project/settings.py"
preserve "requirements.txt"
preserve ".env"

echo "==> git fetch $REMOTE $BRANCH"
git fetch "$REMOTE" "$BRANCH"

# Conflict/merge yo'q: tracked kod origin/main dan olinadi, keyin sozlamalar qaytariladi.
git checkout "$REMOTE/$BRANCH" -- .

restore "xalikova_project/settings.py"
restore "requirements.txt"
restore ".env"

# Keyingi git operatsiyalar ham bu fayllarni yozmasin
git update-index --skip-worktree "xalikova_project/settings.py" 2>/dev/null || true
git update-index --skip-worktree "requirements.txt" 2>/dev/null || true

if grep -q '^<<<<<<< ' "$APP_DIR/xalikova_project/settings.py" 2>/dev/null; then
  echo "XATO: settings.py da hali conflict belgilari bor. Deploy to'xtatildi."
  echo "  JetBackup dan faqat xalikova_project/settings.py ni tiklang."
  exit 1
fi

if [[ -n "${CONDA_PREFIX:-}" ]] || [[ -n "${VIRTUAL_ENV:-}" ]]; then
  PYTHON=python
  echo "==> Muhit: ${CONDA_DEFAULT_ENV:-${VIRTUAL_ENV:-conda/venv}}"
elif [[ -z "$VENV_DIR" ]]; then
  if [[ -d "$APP_DIR/.venv" ]]; then VENV_DIR="$APP_DIR/.venv"; fi
  if [[ -d "$APP_DIR/venv" ]]; then VENV_DIR="$APP_DIR/venv"; fi
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

echo "==> pip o'tkazildi (requirements o'zgarmaydi)"
echo "==> migrate (db.sqlite3 o'chirilmaydi)"
"$PYTHON" manage.py migrate --noinput

echo "==> knowledge index"
if [[ "$FULL_INDEX" == "1" ]]; then
  "$PYTHON" manage.py index_knowledge --full
else
  "$PYTHON" manage.py index_knowledge
fi

echo "==> collectstatic"
"$PYTHON" manage.py collectstatic --noinput

echo "==> check"
"$PYTHON" manage.py check

if [[ -f "$APP_DIR/passenger_wsgi.py" ]] || [[ -d "$APP_DIR/tmp" ]] || [[ -d "$APP_DIR/public" ]]; then
  mkdir -p "$APP_DIR/tmp"
  touch "$APP_DIR/tmp/restart.txt"
  echo "==> Passenger restart"
fi

if [[ -n "$SERVICE_NAME" ]] && command -v systemctl >/dev/null 2>&1; then
  sudo systemctl restart "$SERVICE_NAME"
fi

echo ""
echo "OK. O'zgarmagan: settings.py, requirements.txt, .env, db.sqlite3, media/"
