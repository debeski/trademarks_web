#!/bin/sh
set -e

until nc -z -v -w30 db 5432; do
  echo "Waiting for database..."
  sleep 1
done

# Run the command passed to the container
exec "$@"
