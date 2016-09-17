install:
	pip install -r requirements/production.txt

install_devs:
	pip install -r requirements/local.txt
	pip install -r requirements/test.txt

test:
	time python manage.py test --keepdb

test_parallel:
	time python manage.py test --keepdb --parallel $(grep -c ^processor /proc/cpuinfo)

coverage:
	time python manage.py test --keepdb
	coverage run --branch --omit=*/site-packages/* manage.py test --verbosity=2 --keepdb

coverage_html: coverage
	coverage html
	x-www-browser htmlcov/index.html

server:
	python manage.py runserver

drop_test_databases:
	echo "drop database test_feder; drop database test_feder_1; drop database test_feder_2; drop database test_feder_3; drop database test_feder_4;" | python manage.py dbshell
