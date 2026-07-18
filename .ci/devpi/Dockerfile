FROM python:3.12-slim

RUN pip install --no-cache-dir devpi-server devpi-client

RUN addgroup --system --gid 1000 devpi \
    && adduser --disabled-password --system --uid 1000 \
               --home /data --shell /sbin/nologin \
               --gid 1000 devpi

ENV DEVPISERVER_SERVERDIR=/data

EXPOSE 3141
VOLUME /data

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod 755 /docker-entrypoint.sh

USER devpi
WORKDIR /data

HEALTHCHECK --interval=5s --timeout=3s --start-period=30s --retries=12 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3141/')" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
