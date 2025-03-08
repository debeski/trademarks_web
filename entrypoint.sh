#!/usr/bin/env bash
set -eo pipefail

LOCK_TIMEOUT=60
COMMANDS_RUN_FILE="/app/.commands_run"

# Distributed lock using PostgreSQL
acquire_lock() {
    until psql "$DATABASE_URL" -c "SELECT pg_advisory_lock(123456)"; do
        echo "Waiting for database lock..."
        sleep 1
    done
}

release_lock() {
    psql "$DATABASE_URL" -c "SELECT pg_advisory_unlock(123456)"
}

wait_for_services() {
    for service in "db:5432" "redis:6379"; do
        until nc -z "${service%:*}" "${service#*:}"; do
            echo "Waiting for $service..."
            sleep 1
        done
    done
}

main() {
    wait_for_services
    acquire_lock

    if [[ ! -f "$COMMANDS_RUN_FILE" ]]; then
        echo "----- FIRST RUN INITIALIZATION -----"
        python manage.py collectstatic --noinput
        python manage.py makemigrations users --noinput
        python manage.py makemigrations documents --noinput
        python manage.py migrate --noinput
        python manage.py create_su
        python manage.py populate
        touch "$COMMANDS_RUN_FILE"
        release_lock
    else
        echo "----- WAITING FOR INITIALIZATION -----"
        while [[ ! -f "$COMMANDS_RUN_FILE" ]]; do sleep 5; done
    fi

    echo "----- ROUTINE MIGRATIONS -----"
    python manage.py migrate --noinput

    if [[ "${DEBUG_STATUS,,}" == "true" ]]; then
        exec python manage.py runserver 0.0.0.0:8000
    else
        exec gunicorn -c gunicorn.py
    fi
}

main "$@"
