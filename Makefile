TEST?=feder

.PHONY: docs

clean:
	docker compose down

regenerate_frontend:
	docker compose run --remove-orphans web python manage.py collectstatic --noinput
	docker compose up --remove-orphans gulp --exit-code-from gulp
	docker compose run --remove-orphans web python manage.py collectstatic --noinput

makemessages:
	docker compose run web python manage.py  makemessages --ignore=htmlcov --all

gulp: regenerate_frontend

build:
	docker compose build web gulp

start: wait_mysql
	docker compose up --remove-orphans

test:
	docker compose run web coverage run manage.py test --keepdb --verbosity=2 ${TEST}

coverage_html:
	docker compose run web coverage html

coverage_send:
	docker compose run -e GITHUB_ACTIONS -e GITHUB_REF -e GITHUB_SHA -e GITHUB_HEAD_REF -e GITHUB_REPOSITORY -e GITHUB_RUN_ID -e GITHUB_TOKEN -e COVERALLS_REPO_TOKEN web coveralls

wait_web: wait_mysql

wait_mysql:
	docker compose up -d --remove-orphans db
	docker compose run --remove-orphans web bash -c 'wait-for-it -t 30 db:3306' || (docker compose logs db; exit -1)

migrate:
	docker compose run --remove-orphans web python manage.py migrate

lint: # lint currently staged files
	pre-commit run

lint-all: # lint all files in repository
	pre-commit run --all-files

check: wait_mysql
	docker compose run --remove-orphans web python manage.py makemigrations --check

migrations: wait_mysql
	docker compose run --remove-orphans web python manage.py makemigrations

settings:
	docker compose run --remove-orphans web python manage.py diffsettings

docs:
	docker compose run --remove-orphans web sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html

importterc:
	docker compose run --remove-orphans web sh -c 'curl http://cdn.files.jawne.info.pl/public_html/2017/12/03_05_43_05/TERC_Urzedowy_2017-12-03.xml --output /tmp/TERC.xml && python manage.py load_terc --input /tmp/TERC.xml'

createsuperuser:  # polyfill for django <3. On django 3+ you can use the `DJANGO_SUPERUSER_PASSWORD` env variable.
	docker compose run --remove-orphans web python manage.py createsuperuserwithpassword --username root --email root@example.com --password root --noinput
