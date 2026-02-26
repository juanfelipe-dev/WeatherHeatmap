"""
Management command to fetch and update weather data for all locations.
 
Usage:
    python manage.py fetch_weather
    python manage.py fetch_weather --location-id=1
    python manage.py fetch_weather --forecast-only
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from weather.models import Location
from weather.services import WeatherService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch and update weather data for all or specific locations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--location-id',
            type=int,
            help='Fetch weather for a specific location ID'
        )
        parser.add_argument(
            '--all-locations',
            action='store_true',
            help='Fetch weather for all active locations'
        )
        parser.add_argument(
            '--current-only',
            action='store_true',
            help='Fetch only current weather, not forecast'
        )
        parser.add_argument(
            '--forecast-only',
            action='store_true',
            help='Fetch only forecast, not current weather'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed output'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        service = WeatherService()
        verbose = options.get('verbose', False)
        current_only = options.get('current_only', False)
        forecast_only = options.get('forecast_only', False)
        
        # Determine which locations to fetch
        if options.get('location_id'):
            try:
                locations = [Location.objects.get(id=options['location_id'])]
            except Location.DoesNotExist:
                raise CommandError(f"Location with ID {options['location_id']} not found")
        elif options.get('all_locations'):
            locations = Location.objects.filter(is_active=True)
        else:
            # Default: fetch for first 10 active locations
            locations = Location.objects.filter(is_active=True)[:10]
        
        if not locations:
            self.stdout.write(self.style.WARNING('No active locations found'))
            return
        
        total_locations = len(list(locations))
        self.stdout.write(f'Fetching weather for {total_locations} location(s)...\n')
        
        success_count = 0
        error_count = 0
        
        for location in locations:
            try:
                location_name = f"{location.name} ({location.latitude}, {location.longitude})"
                
                if not forecast_only:
                    weather = service.update_current_weather(location)
                    if weather:
                        if verbose:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✓ Current weather for {location_name}: {weather.temperature}°C, {weather.condition}'
                                )
                            )
                        success_count += 1
                    else:
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(f'⚠ Failed to fetch current weather for {location_name}')
                            )
                        error_count += 1
                
                if not current_only:
                    forecasts = service.update_forecast(location)
                    if forecasts:
                        if verbose:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✓ Forecast for {location_name}: {len(forecasts)} records'
                                )
                            )
                        success_count += 1
                    else:
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(f'⚠ Failed to fetch forecast for {location_name}')
                            )
                        error_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error fetching weather for {location.name}: {str(e)}')
                )
                error_count += 1
                logger.exception(f"Error fetching weather for location {location.id}")
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Successful updates: {success_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Failed updates: {error_count}'))
        self.stdout.write('='*60)
