#!/usr/bin/env python
"""
Setup script for initializing the Weather Heatmap application.
Handles database setup and initial configuration.
"""

import os
import sys
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heatmap_project.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User


def setup_database():
    """Run database migrations."""
    print("🔄 Running database migrations...")
    call_command('migrate', verbosity=2)
    print("✅ Database migrations completed\n")


def create_superuser():
    """Create a superuser if one doesn't exist."""
    if not User.objects.filter(username='admin').exists():
        print("👤 Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'  # Change this in production!
        )
        print("✅ Superuser created (Username: admin, Password: admin123)\n")
    else:
        print("⊘ Superuser 'admin' already exists\n")


def collect_static():
    """Collect static files."""
    print("📦 Collecting static files...")
    call_command('collectstatic', '--noinput', verbosity=1)
    print("✅ Static files collected\n")


def load_sample_data():
    """Load sample locations."""
    print("📍 Loading sample locations...")
    call_command('load_sample_locations', verbosity=2)
    print("✅ Sample locations loaded\n")


def main():
    """Run all setup steps."""
    print("\n" + "="*60)
    print("🌤️  Weather Heatmap - Setup Script")
    print("="*60 + "\n")

    try:
        # Step 1: Database migrations
        setup_database()

        # Step 2: Create superuser
        create_superuser()

        # Step 3: Collect static files
        collect_static()

        # Step 4: Load sample data
        try:
            load_sample_data()
        except Exception as e:
            print(f"⚠️  Warning: Could not load sample data: {e}\n")

        # Final summary
        print("="*60)
        print("✅ Setup Completed Successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Set your WEATHER_API_KEY in .env file")
        print("   Get a free key from: https://openweathermap.org/api")
        print("\n2. Run the development server:")
        print("   python manage.py runserver 0.0.0.0:8000")
        print("\n3. Access the application:")
        print("   - Web Interface: http://localhost:8000/")
        print("   - Admin Panel: http://localhost:8000/admin/")
        print("   - Username: admin")
        print("   - Password: admin123 (CHANGE THIS!)")
        print("\n4. Fetch weather data:")
        print("   python manage.py fetch_weather --verbose")
        print("\n" + "="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
