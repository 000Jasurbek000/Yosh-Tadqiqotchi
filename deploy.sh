#!/usr/bin/env bash
# ============================================================
# Yosh Tadqiqotchi — server deploy
#
# Faqat shuni ishlatish:   bash deploy.sh
# ISHLATMANG:  git pull / git reset --hard / git stash
#
# Serverda o'zgarmaydi:
#   settings.py, requirements.txt, .env, db.sqlite3, media/
# ============================================================

set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="${DEPLOY_BRANCH:-main}"
REMOTE="${DEPLOY_REMOTE:-origin}"
VENV_DIR="${DEPLOY_VENV:-}"
SERVICE_NAME="${DEPLOY_SERVICE:-}"
FULL_INDEX="${DEPLOY_FULL_INDEX:-0}"

cd "$APP_DIR"

KEEP="$(mktemp -d "${TMPDIR:-/tmp}/yt-keep.XXXXXX")"
trap 'rm -rf "$KEEP"' EXIT

save() {
  if [[ -e "$1" ]]; then
    mkdir -p "$KEEP/$(dirname "$1")"
    cp -a "$1" "$KEEP/$1"
    echo "==> saqlandi: $1"
  fi
}

back() {
  if [[ -e "$KEEP/$1" ]]; then
    cp -a "$KEEP/$1" "$1"
    echo "==> qaytarildi: $1"
  fi
}

echo "==> $APP_DIR"

save "xalikova_project/settings.py"
save "requirements.txt"
save ".env"

git update-index --skip-worktree "xalikova_project/settings.py" 2>/dev/null || true
git update-index --skip-worktree "requirements.txt" 2>/dev/null || true

echo "==> git fetch (pull yo'q)"
git fetch "$REMOTE" "$BRANCH"

# Faqat kod: settings.py va requirements.txt GitHubdan yozilmaydi
git checkout "$REMOTE/$BRANCH" -- . \
  ':(exclude)xalikova_project/settings.py' \
  ':(exclude)requirements.txt'

back "xalikova_project/settings.py"
back "requirements.txt"
back ".env"

git update-index --skip-worktree "xalikova_project/settings.py" 2>/dev/null || true
git update-index --skip-worktree "requirements.txt" 2>/dev/null || true

if grep -q '^<<<<<<< ' "xalikova_project/settings.py" 2>/dev/null; then
  echo "XATO: settings.py conflict. Deploy to'xtadi."
  exit 1
fi

if [[ -n "${CONDA_PREFIX:-}" || -n "${VIRTUAL_ENV:-}" ]]; then
  PYTHON=python
elif [[ -f "${VENV_DIR:-}/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  PYTHON=python
elif [[ -d "$APP_DIR/.venv" ]]; then
  # shellcheck source=/dev/null
  source "$APP_DIR/.venv/bin/activate"
  PYTHON=python
else
  PYTHON="${DEPLOY_PYTHON:-python3}"
fi

echo "==> pip yo'q; migrate (sqlite o'chirilmaydi)"
"$PYTHON" manage.py migrate --noinput

echo "==> knowledge index"
if [[ "$FULL_INDEX" == "1" ]]; then
  "$PYTHON" manage.py index_knowledge --full
else
  "$PYTHON" manage.py index_knowledge
fi

echo "==> collectstatic + check"
"$PYTHON" manage.py collectstatic --noinput
"$PYTHON" manage.py check

mkdir -p "$APP_DIR/tmp"
touch "$APP_DIR/tmp/restart.txt"
echo "==> Passenger restart"

echo ""
echo "OK. Serverdagi settings / requirements / .env / db o'zgarmadi."
