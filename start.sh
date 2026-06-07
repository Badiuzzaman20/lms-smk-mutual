#!/bin/bash
set -e

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Seeding initial data ==="
python -X utf8 seed_data.py

echo "=== Starting Gunicorn ==="
gunicorn smk_lms.wsgi --workers 2 --timeout 120 --log-file -
