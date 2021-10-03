TEST?=feder

.PHONY: docs

clean:
	docker-compose down

regenerate_frontend:
	docker-compose up gulp

build:
	docker-compose build web

test:
	docker-compose run web coverage run manage.py test --keepdb --verbosity=2 ${TEST}

test-es:
	docker-compose -f docker-compose.yml -f docker-compose.es.yml run python manage.py test --keepdb --verbosity=2 ${TEST}

coverage_html:
	docker-compose run web coverage html

coverage_send:
	docker-compose run -e GITHUB_ACTIONS -e GITHUB_REF -e GITHUB_SHA -e GITHUB_HEAD_REF -e GITHUB_REPOSITORY -e GITHUB_RUN_ID -e GITHUB_TOKEN -e COVERALLS_REPO_TOKEN web coveralls

migrate:
	docker-compose up migration

lint: # lint currently staged files
	pre-commit run

lint-all: # lint all files in repository
	pre-commit run --all-files

check: wait_mysql
	docker-compose run web python manage.py makemigrations --check

migrations: wait_mysql
	docker-compose run web python manage.py makemigrations

settings:
	docker-compose run web python manage.py diffsettings

docs:
	docker-compose run web sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html

importterc:
	docker-compose run web sh -c 'curl http://cdn.files.jawne.info.pl/public_html/2017/12/03_05_43_05/TERC_Urzedowy_2017-12-03.xml --output /tmp/TERC.xml && python manage.py load_terc --input /tmp/TERC.xml'

createsuperuser:  # polyfill for django <3. On django 3+ you can use the `DJANGO_SUPERUSER_PASSWORD` env variable.
	docker-compose run web python manage.py createsuperuserwithpassword --username root --email root@example.com --password root --noinput
