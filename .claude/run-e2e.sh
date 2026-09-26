#!/bin/bash
# Runs Cypress e2e tests without Docker (equivalent of `make e2e`).
# Requires environment provisioned by .claude/cloud-setup.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
eval "$(feder-env)"
export DATABASE_URL=mysql://root:password@127.0.0.1/test_feder
export TEST=1 ACCOUNT_EMAIL_VERIFICATION=none
[ -e tests/node_modules ] || ln -s /opt/feder-e2e/node_modules tests/node_modules

mysql -h127.0.0.1 -uroot -ppassword -e \
  "CREATE DATABASE IF NOT EXISTS test_feder CHARACTER SET utf8mb4 COLLATE utf8mb4_polish_ci" 2>/dev/null
python manage.py collectstatic --no-input >/dev/null
python manage.py migrate --no-input >/dev/null
python manage.py createsuperuserwithpassword \
  --username e2e --email e2e@example.com --password e2e --noinput || true

python manage.py runserver 0.0.0.0:8000 >logs/e2e-runserver.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT
cd tests
npx wait-on -t 120000 http://web:8000
npx cypress run --e2e "$@"
