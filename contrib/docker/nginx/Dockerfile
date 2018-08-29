FROM nginx:latest
COPY ./contrib/docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=quay.io/watchdogpolska/feder_django:latest /src/feder/static /usr/share/nginx/html/static
