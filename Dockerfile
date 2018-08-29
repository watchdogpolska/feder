FROM python:2.7 as builder
WORKDIR /src
RUN pip install gunicorn
COPY requirements.txt /src/
COPY requirements/*.txt /src/requirements/
RUN pip install -r requirements.txt

FROM builder as javascript
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - \
 && apt-get install -y nodejs
COPY package.json yarn.lock ./
RUN npm install --global yarn
RUN NODE_ENV=development yarn install
#RUN yarn add gulp
COPY . /src
RUN npx gulp icons js scss

FROM builder as app
COPY --from=javascript /src/feder/static /src/feder/static
COPY . /src
CMD gunicorn config.wsgi --bind 0.0.0.0:9000 --capture-output --log-level debug
