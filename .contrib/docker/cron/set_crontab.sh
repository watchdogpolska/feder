
# This script sets up the crontab for the application. To be run when starting app cron container.
APP_ROOT_DIR="${APP_ROOT_DIR:-/code}"
APP_NAME="${APP_NAME:-porady}"
CRON_DIR="${SCRIPT_DIR:-/code/.contrib/docker/cron}"
PTYHON=$(which python3)
SHELL="/bin/bash"

# Set default schedules for the application cron jobs
# The schedules can be overridden by setting the corresponding environment variables
# in app cron container.
# Schedule format: minute hour day month weekday
# or @reboot, @yearly, @annually, @monthly, @weekly, @daily, @midnight, @hourly
UPDATE_EMAILLABS_SCHEDULE="${UPDATE_EMAILLABS_SCHEDULE:-0 */3 * * *}"
CLEARSESSIONS_SCHEDULE="${CLEARSESSIONS_SCHEDULE:-@daily}"
VIRUS_SCAN_SCHEDULE="${VIRUS_SCAN_SCHEDULE:-*/15 * * * *}"

# Set the crontab for the application
echo "
# $APP_NAME-update_emaillabs
$UPDATE_EMAILLABS_SCHEDULE cd $APP_ROOT_DIR && $CRON_DIR/run_locked.sh feder_update_emaillabs 25h \
    \"$PTYHON $APP_ROOT_DIR/manage.py update_emaillabs\" >> /var/log/cron.log 2>&1
# $APP_NAME-clearsessions
$CLEARSESSIONS_SCHEDULE cd $APP_ROOT_DIR && $CRON_DIR/run_locked.sh feder_clearsessions 34h \
    \"$PTYHON $APP_ROOT_DIR/manage.py clearsessions\" >> /var/log/cron.log 2>&1
# $APP_NAME-virus_scan
$VIRUS_SCAN_SCHEDULE cd $APP_ROOT_DIR && $CRON_DIR/run_locked.sh feder_virus_scan 3h \
    \"$PTYHON $APP_ROOT_DIR/manage.py virus_scan\" >> /var/log/cron.log 2>&1
" | crontab -
 
# The  run_locked.sh  script is a simple wrapper around  flock  that ensures that only one 
# instance of a given command is running at a time. 
# Path: .contrib/docker/cron/run_locked.sh