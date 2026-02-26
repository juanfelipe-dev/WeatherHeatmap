#!/usr/bin/env python
"""
Verification script to test the Weather Heatmap implementation.
Run this to verify all components are working correctly.
"""

import os
import sys
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heatmap_project.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from weather.models import Location, WeatherData, WeatherForecast, WeatherAlert
from weather.services import WeatherService


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_status(status, message):
    """Print status message with emoji."""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {message}")


def verify_database():
    """Verify database is working."""
    print_header("Database Verification")
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_status(True, "Database connection successful")
    except Exception as e:
        print_status(False, f"Database connection failed: {e}")
        return False
    
    # Check tables exist
    tables = [
        'weather_location',
        'weather_weatherdata',
        'weather_weatherforecast',
        'weather_weatheralert',
    ]
    
    with connection.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                print_status(True, f"Table '{table}' exists")
            except Exception as e:
                print_status(False, f"Table '{table}' not found: {e}")
                return False
    
    return True


def verify_models():
    """Verify Django models."""
    print_header("Django Models Verification")
    
    try:
        # Check Location model
        locations = Location.objects.all()
        count = locations.count()
        print_status(True, f"Location model works ({count} locations)")
    except Exception as e:
        print_status(False, f"Location model error: {e}")
        return False
    
    try:
        # Check WeatherData model
        weather_data = WeatherData.objects.all()
        count = weather_data.count()
        print_status(True, f"WeatherData model works ({count} records)")
    except Exception as e:
        print_status(False, f"WeatherData model error: {e}")
        return False
    
    try:
        # Check WeatherForecast model
        forecasts = WeatherForecast.objects.all()
        count = forecasts.count()
        print_status(True, f"WeatherForecast model works ({count} records)")
    except Exception as e:
        print_status(False, f"WeatherForecast model error: {e}")
        return False
    
    try:
        # Check WeatherAlert model
        alerts = WeatherAlert.objects.all()
        count = alerts.count()
        print_status(True, f"WeatherAlert model works ({count} records)")
    except Exception as e:
        print_status(False, f"WeatherAlert model error: {e}")
        return False
    
    return True


def verify_data():
    """Verify sample data exists."""
    print_header("Sample Data Verification")
    
    try:
        locations = Location.objects.all()
        if locations.count() == 0:
            print_status(False, "No locations found - run: python manage.py load_sample_locations")
            return False
        
        print_status(True, f"Found {locations.count()} locations")
        
        # List locations
        for loc in locations[:5]:
            print(f"   • {loc.name} ({loc.latitude}, {loc.longitude})")
        
        if locations.count() > 5:
            print(f"   ... and {locations.count() - 5} more")
        
        return True
    except Exception as e:
        print_status(False, f"Error loading locations: {e}")
        return False


def verify_api_client():
    """Verify API client is configured."""
    print_header("API Configuration Verification")
    
    from django.conf import settings
    
    api_key = settings.WEATHER_API_KEY
    if not api_key:
        print_status(False, "WEATHER_API_KEY not configured - add to .env file")
        print("   Get a free key from: https://openweathermap.org/api")
        return False
    
    print_status(True, f"WEATHER_API_KEY is configured (length: {len(api_key)})")
    
    try:
        from weather.services import OpenWeatherMapClient
        client = OpenWeatherMapClient()
        print_status(True, "OpenWeatherMap client initialized")
        return True
    except Exception as e:
        print_status(False, f"Client initialization error: {e}")
        return False


def verify_admin():
    """Verify admin user exists."""
    print_header("Admin User Verification")
    
    try:
        admin = User.objects.get(username='admin')
        print_status(True, f"Admin user exists (email: {admin.email})")
        return True
    except User.DoesNotExist:
        print_status(False, "Admin user not found - run: python manage.py createsuperuser")
        return False
    except Exception as e:
        print_status(False, f"Error checking admin user: {e}")
        return False


def verify_static_files():
    """Verify static files are collected."""
    print_header("Static Files Verification")
    
    static_dir = Path('staticfiles')
    if not static_dir.exists():
        print_status(False, "staticfiles directory not found - run: python manage.py collectstatic")
        return False
    
    static_files = list(static_dir.glob('**/*'))
    static_files = [f for f in static_files if f.is_file()]
    
    if not static_files:
        print_status(False, "No static files found")
        return False
    
    print_status(True, f"Static files collected ({len(static_files)} files)")
    
    # Check for key weather app static files
    key_files = [
        'staticfiles/weather/ui.css',
        'staticfiles/weather/ui.js',
    ]
    
    for file in key_files:
        if Path(file).exists():
            print_status(True, f"Key file found: {file}")
        else:
            print_status(False, f"Key file missing: {file}")
    
    return True


def verify_templates():
    """Verify templates exist."""
    print_header("Template Files Verification")
    
    templates = [
        'weather/templates/weather/base.html',
        'weather/templates/weather/index.html',
        'weather/templates/weather/weather_map.html',
    ]
    
    all_exist = True
    for template in templates:
        if Path(template).exists():
            print_status(True, f"Template found: {template}")
        else:
            print_status(False, f"Template missing: {template}")
            all_exist = False
    
    return all_exist


def verify_imports():
    """Verify all imports work."""
    print_header("Python Imports Verification")
    
    imports = [
        ('django', 'Django'),
        ('rest_framework', 'Django REST Framework'),
        ('requests', 'requests'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_imported = True
    for module, name in imports:
        try:
            __import__(module)
            print_status(True, f"{name} imported successfully")
        except ImportError as e:
            print_status(False, f"{name} import failed: {e}")
            all_imported = False
    
    return all_imported


def main():
    """Run all verifications."""
    print("\n" + "🌤️ " * 15)
    print("WEATHER HEATMAP - IMPLEMENTATION VERIFICATION")
    print("🌤️ " * 15 + "\n")
    
    results = []
    
    # Run all verifications
    results.append(("Imports", verify_imports()))
    results.append(("Database", verify_database()))
    results.append(("Models", verify_models()))
    results.append(("Sample Data", verify_data()))
    results.append(("API Configuration", verify_api_client()))
    results.append(("Admin User", verify_admin()))
    results.append(("Static Files", verify_static_files()))
    results.append(("Templates", verify_templates()))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}\n")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    if passed == total:
        print("\n" + "="*60)
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("="*60)
        print("\n✅ Next Steps:")
        print("  1. Add WEATHER_API_KEY to .env file")
        print("  2. Run: python manage.py fetch_weather")
        print("  3. Visit: http://localhost:8000/")
        print("  4. Admin: http://localhost:8000/admin/")
        print("\n" + "="*60 + "\n")
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️ SOME VERIFICATIONS FAILED")
        print("="*60)
        print("\n❌ Please fix the issues above and try again.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
