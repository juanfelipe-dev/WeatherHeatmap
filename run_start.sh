#!/usr/bin/env bash
set -e

echo "Starting render startup script"

# Wait for the database to be ready and run migrations. Retry on failure.
RETRY_COUNT=0
MAX_RETRIES=30
SLEEP_SECONDS=2

until python manage.py migrate --noinput; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  echo "Migration attempt $RETRY_COUNT failed. Retrying in ${SLEEP_SECONDS}s..."
  if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
    echo "Migrations failed after $MAX_RETRIES attempts. Exiting."
    exit 1
  fi
  sleep $SLEEP_SECONDS
done

echo "Migrations applied successfully"

echo "Collecting static files"
python manage.py collectstatic --noinput || true

echo "Starting Gunicorn"
exec gunicorn heatmap_project.wsgi:application --bind 0.0.0.0:8000
