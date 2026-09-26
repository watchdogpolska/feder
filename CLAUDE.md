# Feder – notes for Claude Code

## Claude Code on the web (cloud environment)

No Docker daemon is available there, so the project runs natively. The
environment is provisioned by `.claude/cloud-setup.sh` – paste its contents
into the cloud environment's **Setup script** field. It also installs
`/etc/profile.d/feder.sh` (sourced from `/root/.bashrc`), which exports the
environment (virtualenv `/opt/feder-venv`,
`DATABASE_URL=mysql://root:password@127.0.0.1/feder`) and starts MySQL in the
background when the session's shell is initialized. If MySQL is not up yet,
run `feder-mysql-start` (waits until it accepts connections).

- Unit tests (equivalent of `make test`):
  `python manage.py test --keepdb --parallel 4 feder`
- Migrations check (`make check`): `python manage.py makemigrations --check --dry-run`
- E2E Cypress tests (`make e2e`): `.claude/run-e2e.sh`
- Dev server: `python manage.py migrate && python manage.py runserver 0.0.0.0:8000`
- Manual env setup in a shell: `eval "$(feder-env)"`

Three `virus_scan` tests are skipped unless `METADEFENDER_API_KEY` is set.

## Local development

Use Docker Compose via the `Makefile` (see `README.rst`).
