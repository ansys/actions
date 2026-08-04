#!/bin/bash
set -e

DEVPI_PASSWORD="${DEVPI_PASSWORD:-devpipass}"
SERVERDIR="${DEVPISERVER_SERVERDIR:-/data}"

wait_for_server() {
    local retries=30
    until python -c "import urllib.request; urllib.request.urlopen('http://localhost:3141/')" 2>/dev/null; do
        retries=$((retries - 1))
        if [ "$retries" -le 0 ]; then
            echo "ERROR: devpi-server did not start in time" >&2
            exit 1
        fi
        sleep 1
    done
}

if [ ! -f "${SERVERDIR}/.serverversion" ]; then
    echo "[INIT] Initializing devpi-server at ${SERVERDIR}..."
    devpi-init --serverdir "${SERVERDIR}"

    echo "[INIT] Starting server temporarily for user/index configuration..."
    devpi-server --host 127.0.0.1 --port 3141 --serverdir "${SERVERDIR}" &
    SERVER_PID=$!
    wait_for_server

    echo "[INIT] Configuring root user and public index..."
    devpi use http://localhost:3141
    devpi login root --password ''
    devpi user -m root password="${DEVPI_PASSWORD}"
    devpi index -y -c public
    devpi logoff

    echo "[INIT] Stopping temporary server..."
    kill "${SERVER_PID}"
    wait "${SERVER_PID}" 2>/dev/null || true
    echo "[INIT] Initialization complete."
fi

echo "[RUN] Starting devpi-server..."
exec devpi-server --host 0.0.0.0 --port 3141 --serverdir "${SERVERDIR}" --restrict-modify root
