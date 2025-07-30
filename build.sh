#!/usr/bin/env bash
# exit on error
set -o errexit

# Set Django settings module
export DJANGO_SETTINGS_MODULE=archive_project.settings

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Build completed successfully!" 