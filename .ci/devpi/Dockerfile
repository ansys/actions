FROM python:3.12-slim

# Refresh the system CA bundle in the base image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576
RUN python -m pip --disable-pip-version-check install --no-cache-dir --no-deps \
    "pip @ https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"

RUN python -m pip install --no-cache-dir devpi-server devpi-client "certifi>=2026.10.19"

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
