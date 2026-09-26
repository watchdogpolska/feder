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
#   * helper `feder-env` which starts MySQL and prints env variables.
#
# The environment snapshot keeps files, not running processes, so MySQL is
# started per session by the SessionStart hook in .claude/settings.json.
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
mysql -uroot <<'SQL' 2>/dev/null || mysql -uroot -ppassword <<'SQL'
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'password';
CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
CREATE DATABASE IF NOT EXISTS feder CHARACTER SET utf8mb4 COLLATE utf8mb4_polish_ci;
FLUSH PRIVILEGES;
SQL
SQL

# Host aliases used by docker-compose service names (e2e tests use db/web).
grep -qE '\sdb(\s|$)' /etc/hosts || echo "127.0.0.1 db web maildump" >> /etc/hosts

# --- Python ----------------------------------------------------------------
python3.12 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip wheel
"$VENV/bin/pip" install -r "$REQ_DIR/requirements/dev.txt"

# --- Cypress (e2e) -----------------------------------------------------------
# tests/ deps are installed to /opt/feder-e2e; the SessionStart hook links
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

# Make the environment available to interactive/login shells as well.
cat > /etc/profile.d/feder.sh <<'SH'
export VIRTUAL_ENV=/opt/feder-venv
export PATH=/opt/feder-venv/bin:$PATH
export DATABASE_URL=${DATABASE_URL:-mysql://root:password@127.0.0.1/feder}
SH
grep -q feder.sh /root/.bashrc 2>/dev/null || echo '. /etc/profile.d/feder.sh' >> /root/.bashrc

service mysql stop || true
echo "feder setup done"
