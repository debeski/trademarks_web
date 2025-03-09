#!/usr/bin/env bash
set -eo pipefail

# Read secrets into environment variables
# export POSTGRES_PASSWORD=$(cat /run/secrets/POSTGRES_PASSWORD)
# export DJANGO_SECRET_KEY=$(cat /run/secrets/DJANGO_SECRET_KEY)

# Construct DATABASE_URL using environment variables from default-environment
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"

LOCK_TIMEOUT=300
INIT_LOCK_FILE="/app/.init.lock"

# Distributed lock using PostgreSQL advisory lock
acquire_lock() {
    echo "Attempting to acquire initialization lock..."
    while true; do
        echo "Checking lock..."
        psql "$DATABASE_URL" -c "SET statement_timeout = 5000; SELECT pg_try_advisory_xact_lock(123456)"
        if psql "$DATABASE_URL" -t -c "SELECT pg_try_advisory_xact_lock(123456)" | grep -q 't'; then
            echo "Lock acquired"
            return 0
        fi
        echo "Waiting for initialization lock..."
        sleep 5
    done
}

release_lock() {
    echo "Releasing lock"
    psql "$DATABASE_URL" -c "SELECT pg_advisory_unlock(123456)" || true
}

check_migrations() {
    python manage.py showmigrations --plan | grep -q '\[ \]'
}

perform_initialization() {
    echo "----- PERFORMING INITIALIZATION -----"
    
    # Collect static files with atomic operation
    python manage.py collectstatic --noinput --clear
    
    # Create migrations if needed
    if ! python manage.py makemigrations --check --noinput; then
        python manage.py makemigrations users documents --noinput
        python manage.py makemigrations --noinput
    fi
    
    # Apply migrations
    python manage.py migrate --noinput
    
    # Create superuser
    python manage.py create_su
    
    # Populate initial data
    python manage.py populate
    
    touch $INIT_LOCK_FILE
}

wait_for_services() {
    for service in "db:5432" "redis:6379"; do
        until nc -zw 2 "${service%:*}" "${service#*:}"; do
            echo "Waiting for $service..."
            sleep 2
        done
    done
}

main() {
    wait_for_services
    
    # Only perform initialization once across all replicas
    if [ ! -f $INIT_LOCK_FILE ]; then
        acquire_lock
        trap release_lock EXIT
    
        # Double-check after acquiring lock
        if [ ! -f $INIT_LOCK_FILE ]; then
            perform_initialization
        else
            echo "Initialization already completed by another instance"
        fi
    else
        echo "Initialization already completed"
    fi

    # Regular startup
    echo "----- STARTING APPLICATION -----"
    exec "$@"
}

main "$@"
