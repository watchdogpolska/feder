ARG PYTHON_VERSION='3.6'
FROM python:${PYTHON_VERSION}-slim as build
RUN mkdir /code
WORKDIR /code

# Install python dependencies
ENV PYTHONUNBUFFERED 1
RUN apt-get update \
&& apt-get install -y --no-install-recommends \
   default-libmysqlclient-dev \
   gcc \
   build-essential \
   git \
   curl \
   gettext libgettextpo-dev \
&& rm -rf /var/lib/apt/lists/*
COPY requirements/*.txt ./requirements/
ARG DJANGO_VERSION='==2.22.*'
FROM build as development
# TODO: Move to /requirements/base.txt after fixing following bug:
#       https://github.com/readthedocs/readthedocs-docker-images/issues/158
RUN pip install mysqlclient==2.0.3
RUN bash -c "if [[ \"${DJANGO_VERSION}\" == 'master' ]]; then \
pip install --no-cache-dir -r requirements/dev.txt https://github.com/django/django/archive/master.tar.gz; else \
pip install --no-cache-dir -r requirements/dev.txt \"django${DJANGO_VERSION}\"; fi"
COPY ./ /code/
CMD python manage.py runserver 0.0.0.0:8000
FROM build as production
ENV DJANGO_SETTINGS_MODULE="config.settings.production"
RUN pip install --no-cache-dir mysqlclient==2.0.3 -r requirements/production.txt
COPY ./ /code/
RUN DJANGO_SECRET_KEY=x \
   DJANGO_SERVER_EMAIL=x \
   DATABASE_URL=sqlite:// \
   EMAILLABS_APP_KEY=x \
   EMAILLABS_SECRET_KEY=x \
   LETTER_RECEIVE_SECRET=x \
   AWS_S3_ACCESS_KEY_ID=x \
   AWS_S3_SECRET_ACCESS_KEY=x \
   AWS_STORAGE_BUCKET_NAME=x \
   python manage.py collectstatic --no-input
CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "config.wsgi"]
