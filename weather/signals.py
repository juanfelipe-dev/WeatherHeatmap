"""
Django signals for weather application.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import WeatherData, WeatherAlert

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WeatherData)
def on_weather_data_saved(sender, instance, created, **kwargs):
    """Handle actions when weather data is saved."""
    # You can add post-processing logic here
    # For example: trigger notifications, update related data, etc.
    pass


@receiver(post_save, sender=WeatherAlert)
def on_weather_alert_saved(sender, instance, created, **kwargs):
    """Handle actions when weather alert is saved."""
    if created:
        logger.info(f"New weather alert created: {instance.alert_type} for {instance.location.name}")
    else:
        logger.info(f"Weather alert updated: {instance.alert_type}")
