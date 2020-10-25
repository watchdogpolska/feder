TEST?=feder

.PHONY: docs

clean:
	docker-compose down

regenerate_frontend:
	docker-compose run web python manage.py collectstatic -c --noinput
	docker-compose up gulp

build:
	docker-compose build web

test:
	docker-compose run web coverage run manage.py test --keepdb --verbosity=2 ${TEST}

coverage_html:
	docker-compose run web coverage html

coverage_send:
	docker-compose run -e GITHUB_ACTIONS -e GITHUB_REF -e GITHUB_SHA -e GITHUB_HEAD_REF -e GITHUB_REPOSITORY -e GITHUB_RUN_ID -e GITHUB_TOKEN -e COVERALLS_REPO_TOKEN web coveralls

wait_web: wait_mysql wait_elasticsearch wait_tika

wait_mysql:
	docker-compose up -d db
	docker-compose run web bash -c 'wait-for-it -t 30 db:3306' || (docker-compose logs db; exit -1)

wait_elasticsearch:
	docker-compose up -d elasticsearch
	docker-compose run web bash -c 'wait-for-it -t 30 elasticsearch:9200' || (docker-compose logs elasticsearch; exit -1)

wait_tika:
	docker-compose up -d tika
	docker-compose run web bash -c 'wait-for-it -t 60 tika:9998' || (docker-compose logs tika; exit -1)

migrate:
	docker-compose run web python manage.py migrate

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

create_fake_socialapp:  # unblock the login screen in a local deployment. To be executed once, on a fresh database. To be used only in debug environments.
	docker-compose run web python manage.py create_social_app
