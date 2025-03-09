#!/usr/bin/env bash
set -eo pipefail

# Read secrets into environment variables
# export POSTGRES_PASSWORD=$(cat /run/secrets/POSTGRES_PASSWORD)
# export DJANGO_SECRET_KEY=$(cat /run/secrets/DJANGO_SECRET_KEY)

# Construct DATABASE_URL using environment variables from default-environment
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"

LOCK_TIMEOUT=60
COMMANDS_RUN_FILE="/app/.commands_run"

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
    # Execute the command passed to the container
    exec "$@"
}

main "$@"
