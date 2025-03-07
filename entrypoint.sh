#!/usr/bin/env bash

COMMANDS_RUN_FILE="/app/.commands_run"

wait_for_service() {
    host=$1
    port=$2
    echo "Waiting for $host:$port..."
    while ! python -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('$host', $port))" 2>/dev/null; do
        sleep 1
    done
}

if [ ! -f "$COMMANDS_RUN_FILE" ]; then
    wait_for_service db 5432
    wait_for_service redis 6379
    
    echo "Running management commands..."
    python manage.py collectstatic --noinput
    python manage.py makemigrations users
    python manage.py makemigrations documents
    python manage.py makemigrations
    python manage.py migrate
    python manage.py create_su
    python manage.py populate

    touch "$COMMANDS_RUN_FILE"
fi



# Apply database migrations
python manage.py migrate --noinput

# Start Django server in the background
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 &

# Start Celery worker in the background
python -m celery -A core worker --loglevel=info &

# Keep container running
wait