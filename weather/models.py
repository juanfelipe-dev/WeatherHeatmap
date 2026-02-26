"""
Weather data models for storing and managing weather information.
"""

from django.db import models
from django.utils import timezone


class Location(models.Model):
    """Geographic location for weather data collection."""
    name = models.CharField(max_length=255, unique=True, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # Optional: Use GeoDjango PointField for GIS operations
    # geometry = gis_models.PointField(null=True, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class WeatherData(models.Model):
    """Current and historical weather data."""
    CONDITION_CHOICES = [
        ('clear', 'Clear'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('snowy', 'Snowy'),
        ('stormy', 'Stormy'),
        ('foggy', 'Foggy'),
        ('unknown', 'Unknown'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_data')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Temperature data
    temperature = models.FloatField(help_text="Temperature in Celsius")
    feels_like = models.FloatField(null=True, blank=True, help_text="Feels like temperature in Celsius")
    temp_min = models.FloatField(null=True, blank=True, help_text="Minimum temperature in Celsius")
    temp_max = models.FloatField(null=True, blank=True, help_text="Maximum temperature in Celsius")
    
    # Atmospheric data
    humidity = models.IntegerField(help_text="Humidity percentage (0-100)")
    pressure = models.IntegerField(help_text="Atmospheric pressure in hPa")
    wind_speed = models.FloatField(help_text="Wind speed in m/s")
    wind_direction = models.IntegerField(null=True, blank=True, help_text="Wind direction in degrees (0-360)")
    
    # Precipitation
    precipitation = models.FloatField(default=0, help_text="Precipitation in mm")
    cloudiness = models.IntegerField(default=0, help_text="Cloud coverage percentage (0-100)")
    
    # Visibility and conditions
    visibility = models.IntegerField(null=True, blank=True, help_text="Visibility in meters")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='unknown')
    condition_description = models.CharField(max_length=255, blank=True)
    
    # UV Index
    uv_index = models.FloatField(null=True, blank=True)
    
    # API response data (store raw JSON for debugging)
    raw_data = models.JSONField(default=dict, blank=True)
    
    # Metadata
    api_source = models.CharField(max_length=50, default='openweathermap')
    is_current = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['location', '-timestamp']),
            models.Index(fields=['is_current']),
        ]
        verbose_name_plural = 'Weather data'

    def __str__(self):
        return f"{self.location.name} - {self.temperature}°C at {self.timestamp}"

    @property
    def temperature_fahrenheit(self):
        """Convert temperature from Celsius to Fahrenheit."""
        return (self.temperature * 9/5) + 32

    @property
    def wind_speed_kmh(self):
        """Convert wind speed from m/s to km/h."""
        return self.wind_speed * 3.6


class WeatherAlert(models.Model):
    """Weather alerts and warnings for locations."""
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_alerts')
    alert_type = models.CharField(max_length=100)  # e.g., 'Heat Wave', 'Frost Warning', etc.
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location', 'is_active']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"{self.alert_type} - {self.location.name}"

    @property
    def is_current(self):
        """Check if alert is currently active."""
        now = timezone.now()
        return self.is_active and self.start_time <= now and (self.end_time is None or now <= self.end_time)


class WeatherForecast(models.Model):
    """Weather forecast data for future time periods."""
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='forecasts')
    forecast_time = models.DateTimeField(db_index=True)  # Time this forecast is for
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Forecast data
    temperature = models.FloatField()
    temp_min = models.FloatField(null=True, blank=True)
    temp_max = models.FloatField(null=True, blank=True)
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    wind_direction = models.IntegerField(null=True, blank=True)
    precipitation_probability = models.IntegerField(default=0, help_text="Precipitation probability (0-100)")
    precipitation = models.FloatField(default=0, help_text="Expected precipitation in mm")
    cloudiness = models.IntegerField(default=0)
    condition = models.CharField(max_length=20, choices=WeatherData.CONDITION_CHOICES)
    condition_description = models.CharField(max_length=255, blank=True)
    
    raw_data = models.JSONField(default=dict, blank=True)
    api_source = models.CharField(max_length=50, default='openweathermap')

    class Meta:
        ordering = ['forecast_time']
        indexes = [
            models.Index(fields=['location', 'forecast_time']),
        ]
        unique_together = [['location', 'forecast_time']]

    def __str__(self):
        return f"{self.location.name} - {self.temperature}°C at {self.forecast_time}"
