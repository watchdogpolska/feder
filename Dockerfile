# This is Dockerfile for development purposes only.
ARG PYTHON_VERSION='3'
FROM python:${PYTHON_VERSION}-slim
RUN mkdir /code
WORKDIR /code

# Install python dependencies
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE="config.settings.production"
RUN apt-get update \
&& apt-get install -y --no-install-recommends \
   default-libmysqlclient-dev \
   gcc \
   build-essential \
   git \
   curl \
   gettext libgettextpo-dev wait-for-it \
&& rm -rf /var/lib/apt/lists/*
COPY requirements/*.txt ./requirements/
ARG DJANGO_VERSION='==2.22.*'
# TODO: Move to /requirements/base.txt after fixing following bug:
#       https://github.com/readthedocs/readthedocs-docker-images/issues/158
RUN pip install --no-cache-dir mysqlclient==2.0.3 -r requirements/production.txt
COPY ./ /code/
RUN DJANGO_SECRET_KEY=x \
   DJANGO_SERVER_EMAIL=x \
   DATABASE_URL=sqlite:// \
   EMAILLABS_APP_KEY=x \
   EMAILLABS_SECRET_KEY=x \
   LETTER_RECEIVE_SECRET=x \
   python manage.py collectstatic --no-input
CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "config.wsgi"]
