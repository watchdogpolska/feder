#!/bin/bash
# Setup script for Claude Code on the web (cloud environment).
#
# Paste the contents of this file into: environment settings -> "Setup script".
# See https://code.claude.com/docs/en/cloud-environments#setup-scripts
#
# It provisions the VM natively (no Docker daemon is available):
#   * MySQL 8.0 server configured like the `db` service in docker-compose.yml,
#   * Python 3.12 virtualenv in /opt/feder-venv with requirements/dev.txt,
#   * Cypress + Xvfb for e2e tests (tests/),
#   * helpers: `feder-env` (starts MySQL, prints env variables),
#     `feder-mysql-start` and `feder-e2e` (Cypress e2e run, like `make e2e`),
#   * /root/.claude/CLAUDE.md with instructions for Claude Code,
#   * /etc/profile.d/feder.sh, sourced from /root/.bashrc, which exports the
#     environment and starts MySQL in the background.
#
# The environment snapshot keeps files, not running processes. Claude Code
# builds its shell from /root/.bashrc at session start, so MySQL is started
# there, without any extra session start configuration.
set -euo pipefail

REPO_URL="https://github.com/watchdogpolska/feder.git"
REPO_REF="${FEDER_SETUP_REF:-master}"
VENV=/opt/feder-venv
export DEBIAN_FRONTEND=noninteractive

# Requirements are taken from the checked-out repo when present, otherwise
# from a shallow clone (the setup script may run before the repo is cloned).
REQ_DIR=""
for d in "${CLAUDE_PROJECT_DIR:-}" /home/user/feder "$PWD"; do
  if [ -n "$d" ] && [ -f "$d/requirements/dev.txt" ]; then REQ_DIR="$d"; break; fi
done
if [ -z "$REQ_DIR" ]; then
  REQ_DIR=$(mktemp -d)
  git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$REQ_DIR" \
    || git clone --depth 1 "$REPO_URL" "$REQ_DIR"
fi

# --- System packages -------------------------------------------------------
apt-get update
apt-get install -y --no-install-recommends \
  mysql-server-8.0 mysql-client-8.0 libmysqlclient-dev pkg-config \
  build-essential python3.12 python3.12-dev python3.12-venv \
  gettext libgettextpo-dev libssl-dev git curl wait-for-it \
  xvfb libgtk-3-0t64 libgbm1 libnotify4 libnss3 libxss1 libxtst6 \
  libasound2t64 xauth

# --- MySQL (mirrors docker-compose.yml `db` service) ------------------------
cat > /etc/mysql/mysql.conf.d/zz-feder.cnf <<'CNF'
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_polish_ci
max_allowed_packet = 1024M
bind-address = 127.0.0.1
CNF

cat > /usr/local/bin/feder-mysql-start <<'SH'
#!/bin/bash
# Start MySQL if it is not running and wait until it accepts connections.
set -e
if ! mysqladmin --protocol=tcp -h127.0.0.1 -uroot -ppassword ping >/dev/null 2>&1 \
   && ! mysqladmin -uroot ping >/dev/null 2>&1; then
  mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
  (service mysql start || (nohup mysqld_safe >/var/log/mysql/safe.log 2>&1 &)) >/dev/null 2>&1
fi
for _ in $(seq 1 60); do
  mysqladmin --protocol=tcp -h127.0.0.1 -uroot -ppassword ping >/dev/null 2>&1 && exit 0
  mysqladmin -uroot ping >/dev/null 2>&1 && exit 0
  sleep 1
done
echo "MySQL did not start" >&2
exit 1
SH
chmod +x /usr/local/bin/feder-mysql-start
/usr/local/bin/feder-mysql-start

# root/password over TCP, as expected by DATABASE_URL and tests/cypress.
MYSQL_INIT="
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'password';
CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
CREATE DATABASE IF NOT EXISTS feder CHARACTER SET utf8mb4 COLLATE utf8mb4_polish_ci;
FLUSH PRIVILEGES;"
# Fresh install uses auth_socket for root; on re-runs the password is already set.
mysql -uroot -e "$MYSQL_INIT" 2>/dev/null || mysql -uroot -ppassword -e "$MYSQL_INIT"

# Host aliases used by docker-compose service names (e2e tests use db/web).
grep -qE '\sdb(\s|$)' /etc/hosts || echo "127.0.0.1 db web maildump" >> /etc/hosts

# --- Python ----------------------------------------------------------------
python3.12 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip wheel
"$VENV/bin/pip" install -r "$REQ_DIR/requirements/dev.txt"

# --- Cypress (e2e) -----------------------------------------------------------
# tests/ deps are installed to /opt/feder-e2e; `feder-e2e` links
# tests/node_modules to it. The Cypress binary is downloaded with resume and
# retries because a single large download may be cut off by the proxy.
mkdir -p /opt/feder-e2e
cp "$REQ_DIR/tests/package.json" /opt/feder-e2e/
(cd /opt/feder-e2e && CYPRESS_INSTALL_BINARY=0 npm install --no-audit --no-fund)
CY_VER=$(node -p "require('/opt/feder-e2e/node_modules/cypress/package.json').version")
CY_ZIP=/tmp/cypress-$CY_VER.zip
for _ in 1 2 3 4 5; do
  curl -fsSL --retry 5 -C - -o "$CY_ZIP" \
    "https://download.cypress.io/desktop/$CY_VER?platform=linux&arch=x64" \
    && (cd /opt/feder-e2e && CYPRESS_INSTALL_BINARY="$CY_ZIP" npx cypress install --force) \
    && break
  rm -f "$CY_ZIP"; sleep 3
done
rm -f "$CY_ZIP"
(cd /opt/feder-e2e && npx cypress verify) || echo "WARNING: Cypress not verified, e2e tests unavailable"

# --- Session environment helper ---------------------------------------------
cat > /usr/local/bin/feder-env <<'SH'
#!/bin/bash
# Starts MySQL and prints `export` lines for the feder dev/test environment.
/usr/local/bin/feder-mysql-start >&2
cat <<ENV
export VIRTUAL_ENV=/opt/feder-venv
export PATH=/opt/feder-venv/bin:\$PATH
export DJANGO_SETTINGS_MODULE=config.settings.local
export DATABASE_URL=mysql://root:password@127.0.0.1/feder
export DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
export MEDIA_ROOT_ENV=media_dev
export APP_MODE=DEV
ENV
SH
chmod +x /usr/local/bin/feder-env

# Environment for every shell. Claude Code sources /root/.bashrc when a session
# starts, so this also brings MySQL up (in the background, not to block it).
cat > /etc/profile.d/feder.sh <<'SH'
export VIRTUAL_ENV=/opt/feder-venv
case ":$PATH:" in *":/opt/feder-venv/bin:"*) ;; *) export PATH=/opt/feder-venv/bin:$PATH ;; esac
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.local}
export DATABASE_URL=${DATABASE_URL:-mysql://root:password@127.0.0.1/feder}
export DJANGO_EMAIL_BACKEND=${DJANGO_EMAIL_BACKEND:-django.core.mail.backends.console.EmailBackend}
export MEDIA_ROOT_ENV=${MEDIA_ROOT_ENV:-media_dev}
export APP_MODE=${APP_MODE:-DEV}
if ! pgrep -x mysqld >/dev/null 2>&1; then
  (setsid /usr/local/bin/feder-mysql-start >/tmp/feder-mysql-start.log 2>&1 &)
fi
SH
grep -q feder.sh /root/.bashrc 2>/dev/null || echo '. /etc/profile.d/feder.sh' >> /root/.bashrc

# --- E2E runner (equivalent of `make e2e`, without Docker) --------------------
cat > /usr/local/bin/feder-e2e <<'SH'
#!/bin/bash
# Usage: feder-e2e [cypress run args...]   (run from the feder checkout)
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
[ -f manage.py ] || { echo "feder-e2e: run it inside the feder repository" >&2; exit 1; }
eval "$(feder-env)"
export DATABASE_URL=mysql://root:password@127.0.0.1/test_feder
export TEST=1 ACCOUNT_EMAIL_VERIFICATION=none
[ -e tests/node_modules ] || ln -s /opt/feder-e2e/node_modules tests/node_modules

mysql -h127.0.0.1 -uroot -ppassword -e \
  "CREATE DATABASE IF NOT EXISTS test_feder CHARACTER SET utf8mb4 COLLATE utf8mb4_polish_ci" 2>/dev/null
python manage.py collectstatic --no-input >/dev/null
python manage.py migrate --no-input >/dev/null
python manage.py createsuperuserwithpassword \
  --username e2e --email e2e@example.com --password e2e --noinput 2>/dev/null || true

python manage.py runserver 0.0.0.0:8000 >logs/e2e-runserver.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT
cd tests
npx wait-on -t 120000 http://web:8000
npx cypress run --e2e "$@"
SH
chmod +x /usr/local/bin/feder-e2e

# --- Instructions for Claude Code (user memory, loaded in every session) ------
mkdir -p /root/.claude
touch /root/.claude/CLAUDE.md
sed -i '/<!-- feder-setup:begin -->/,/<!-- feder-setup:end -->/d' /root/.claude/CLAUDE.md
cat >> /root/.claude/CLAUDE.md <<'MD'
<!-- feder-setup:begin -->
# Feder (watchdogpolska/feder) – cloud environment

No Docker daemon is available here, so the project runs natively (the
`Makefile` / `docker compose` targets do not work). The cloud environment
setup script provisioned:

- MySQL 8.0 (`root`/`password`, utf8mb4_polish_ci), started in the background
  when the shell is initialized (`/etc/profile.d/feder.sh`, sourced from
  `/root/.bashrc`). If it is not up yet run `feder-mysql-start` (waits).
- Python 3.12 virtualenv `/opt/feder-venv` with `requirements/dev.txt`,
  already on `PATH`; `DATABASE_URL=mysql://root:password@127.0.0.1/feder`.
  If `requirements/*.txt` change, run `pip install -r requirements/dev.txt`.
- Cypress in `/opt/feder-e2e`; hosts `db` and `web` resolve to 127.0.0.1.

Commands (run in the repository root):

- Unit tests (`make test`): `python manage.py test --keepdb --parallel 4 feder`
  (single module: `python manage.py test --keepdb feder.letters`)
- Migrations check (`make check`): `python manage.py makemigrations --check --dry-run`
- E2E Cypress tests (`make e2e`): `feder-e2e`
- Lint (`make lint`): `pre-commit run --all-files`
- Dev server: `python manage.py migrate && python manage.py runserver 0.0.0.0:8000`
- Env in a fresh shell: `eval "$(feder-env)"`

Three `virus_scan` tests are skipped unless `METADEFENDER_API_KEY` is set.
<!-- feder-setup:end -->
MD

service mysql stop || true
echo "feder setup done"
