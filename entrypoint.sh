#!/usr/bin/env bash
set -eo pipefail

# Read secrets into environment variables
# export POSTGRES_PASSWORD=$(cat /run/secrets/POSTGRES_PASSWORD)
# export DJANGO_SECRET_KEY=$(cat /run/secrets/DJANGO_SECRET_KEY)

# Construct DATABASE_URL using environment variables from default-environment
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"

LOCK_TIMEOUT=60
# COMMANDS_RUN_FILE="/app/.commands_run"

acquire_lock() {
    local timeout=30
    local start_time=$(date +%s)
    
    while ! psql "$DATABASE_URL" -c "SELECT pg_try_advisory_lock(123456)" | grep -q 't'; do
        echo "Waiting for database lock..."
        sleep 1
        
        if [ $(($(date +%s) - start_time)) -ge $timeout ]; then
            echo "Lock acquisition timeout reached. Proceeding anyway."
            break
        fi
    done
}

release_lock() {
    psql "$DATABASE_URL" -c "SELECT pg_advisory_unlock(123456)" || true
}

check_initialization() {
    psql "$DATABASE_URL" <<-EOSQL
    CREATE TABLE IF NOT EXISTS app_initialization (
        id SERIAL PRIMARY KEY,
        initialized BOOLEAN NOT NULL DEFAULT false,
        initialized_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO app_initialization (initialized) 
    SELECT false
    WHERE NOT EXISTS (SELECT 1 FROM app_initialization);
EOSQL

    psql "$DATABASE_URL" -t -c "SELECT initialized FROM app_initialization LIMIT 1" | grep -q 't'
}

mark_initialized() {
    psql "$DATABASE_URL" -c "UPDATE app_initialization SET initialized = true"
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
    trap release_lock EXIT
    wait_for_services
    acquire_lock

    if ! check_initialization; then
        echo "----- FIRST RUN INITIALIZATION -----"
        python manage.py collectstatic --noinput

        # Conditional makemigrations
        python manage.py makemigrations --noinput --check || {
            echo "Creating missing migrations..."
            python manage.py makemigrations users documents --noinput
        }
        python manage.py migrate --noinput
        python manage.py create_su
        python manage.py populate
        mark_initialized
    fi

    echo "----- ROUTINE MIGRATIONS -----"
    python manage.py migrate --noinput

    # Execute the command passed to the container
    exec "$@"
}

main "$@"
