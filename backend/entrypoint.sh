#!/bin/sh

# Abort the script if any command fails
set -e

# Check if DJANGO_SETTINGS_MODULE is set
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  echo "Error: DJANGO_SETTINGS_MODULE is not set."
  exit 1
fi

echo "Waiting for the database..."
python manage.py wait_for_db

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Executes the main command of the container
exec "$@"
