#!/bin/bash

# Weather Heatmap - Application Startup Script
# Usage: ./run_start.sh

set -e  # Exit on any error

echo "========================================"
echo "Weather Heatmap - Starting Application"
echo "========================================"

# Run database migrations
echo ""
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Load US cities (optional - comment out if not needed)
echo ""
echo "Loading US cities..."
python manage.py load_us_cities

# Start Gunicorn server
echo ""
echo "Starting Gunicorn server..."
echo "Server will be available at http://0.0.0.0:8000"
echo ""

gunicorn heatmap_project.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
