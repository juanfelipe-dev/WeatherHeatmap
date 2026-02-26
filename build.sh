#!/bin/bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Checking Django setup..."
python manage.py check

echo "Build complete!"
