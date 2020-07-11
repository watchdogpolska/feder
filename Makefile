TEST?=feder

.PHONY: docs

clean:
	docker-compose down

build:
	docker-compose build web

test:
	docker-compose run web coverage run manage.py test --keepdb --verbosity=2 ${TEST}

coverage_html:
	docker-compose run web coverage html

coverage_send:
	docker-compose run -e GITHUB_ACTIONS -e GITHUB_REF -e GITHUB_SHA -e GITHUB_HEAD_REF -e GITHUB_REPOSITORY -e GITHUB_RUN_ID -e GITHUB_TOKEN web coveralls

wait_mysql:
	docker-compose up -d db
	docker-compose run web bash -c 'wait-for-it db:3306'

wait_elasticsearch:
	docker-compose up -d elasticsearch
	docker-compose run web bash -c 'wait-for-it elasticsearch:9200'

wait_tika:
	docker-compose up -d tika
	docker-compose run web bash -c 'wait-for-it tika:9998'

migrate:
	docker-compose run web python manage.py migrate

pyupgrade:
	docker run --rm -v $$(pwd):/data quay.io/watchdogpolska/pyupgrade

lint: pyupgrade
	docker run --rm -v $$(pwd):/apps alpine/flake8 .
	docker run --rm -v $$(pwd):/data cytopia/black --check /data

fmt:
	docker run --rm -v $$(pwd):/data cytopia/black /data

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

createsuperuser:
	docker-compose run -e DJANGO_SUPERUSER_PASSWORD=root web python manage.py createsuperuser --username root --email root@example.com --noinput
