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
    
    echo "Executing First Launch Database Migrations..."
    python manage.py makemigrations users --noinput
    python manage.py makemigrations documents --noinput
    python manage.py migrate --noinput
    python manage.py create_su --noinput
    python manage.py populate --noinput

    touch "$COMMANDS_RUN_FILE"
fi

echo "Attempting Static Files Collection..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Executing Routine Database Migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Start Django server in the background
echo "Launching WSGI server..."
# PRODUCTION
gunicorn -c gunicorn.py &

# # DEVELOPMENT
# python manage.py runserver &

# Start Celery worker in the background
echo "Launching Celery server..."
python -m celery -A core worker --loglevel=info &

# Keep container running
wait