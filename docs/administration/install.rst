.. _installation:

******************
Instalacja
******************

The steps below will get you up and running with a local development environment. We assume you have the following installed
First make sure to install all requires OS-level libraries and application (dependencies)::

    $ sudo apt-get install python2.7 pip mariadb-server git libmariadb-client-lgpl-dev virtualenv python-dev libffi-dev libssl-dev libjpeg-dev libpng12-dev libxml2-dev libxslt1-dev build-essential libjpeg62

Next to create and activate a virtualenv_::

    $ virtualenv env
    $ source env/bin/activate

    .. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Next to open a terminal at the project root and install the requirements for local development::

    $ pip install pip wheel -U
    $ pip install -r requirements/local.txt

Next to create MySQL database::

    # if you are using Ubuntu 14.04, you may need to find a workaround for the following two commands
    $ sudo systemctl start mariadb
    $ sudo systemctl enable mariadb
    
    $ mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql
    
    $ echo "CREATE DATABASE feder CHARACTER SET utf8 COLLATE utf8_polish_ci;" | mysql -u root
    $ echo "CREATE USER 'user'@'localhost' IDENTIFIED BY 'pass';" | mysql -u root
    $ echo "GRANT ALL PRIVILEGES ON feder . * TO 'user'@'localhost'; FLUSH PRIVILEGES;" | mysql -u root

Next to set up enviroment variables::

    $ export DJANGO_SETTINGS_MODULE="config.local"
    $ export DATABASE_URL="mysql://user:pass@localhost/feder"

Next to push migrations into database::

    $ python poradnia/manage.py migrate

You can now run the usual Django ``runserver`` command::

    $ python poradnia/manage.py runserver

To run tests use::

    $ pip install -r requirements/test.txt 
    $ python manage.py test $@ -v2
