"""
Management command to load sample weather locations.

Usage:
    python manage.py load_sample_locations
"""

from django.core.management.base import BaseCommand
from weather.models import Location


SAMPLE_LOCATIONS = [
    {
        'name': 'San Francisco',
        'latitude': 37.7749,
        'longitude': -122.4194,
        'city': 'San Francisco',
        'country': 'United States',
        'timezone': 'America/Los_Angeles',
    },
    {
        'name': 'Seattle',
        'latitude': 47.6062,
        'longitude': -122.3321,
        'city': 'Seattle',
        'country': 'United States',
        'timezone': 'America/Los_Angeles',
    },
    {
        'name': 'Denver',
        'latitude': 39.7392,
        'longitude': -104.9903,
        'city': 'Denver',
        'country': 'United States',
        'timezone': 'America/Denver',
    },
    {
        'name': 'Kansas City',
        'latitude': 39.0997,
        'longitude': -94.5786,
        'city': 'Kansas City',
        'country': 'United States',
        'timezone': 'America/Chicago',
    },
    {
        'name': 'Detroit',
        'latitude': 42.3314,
        'longitude': -83.0458,
        'city': 'Detroit',
        'country': 'United States',
        'timezone': 'America/Detroit',
    },
    {
        'name': 'Phoenix',
        'latitude': 33.4484,
        'longitude': -112.0742,
        'city': 'Phoenix',
        'country': 'United States',
        'timezone': 'America/Phoenix',
    },
]


class Command(BaseCommand):
    help = 'Load sample weather locations into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing locations before loading samples',
        )

    def handle(self, *args, **options):
        if options.get('clear'):
            count, _ = Location.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {count} existing locations')
            )

        created_count = 0
        skipped_count = 0

        for location_data in SAMPLE_LOCATIONS:
            location, created = Location.objects.get_or_create(
                name=location_data['name'],
                defaults=location_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created location: {location.name} ({location.latitude}, {location.longitude})'
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'⊘ Location already exists: {location.name}')
                )
                skipped_count += 1

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} locations'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} locations'))
        self.stdout.write('='*60)

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\nSample locations loaded! Run "python manage.py fetch_weather" to get current data.'
                )
            )
