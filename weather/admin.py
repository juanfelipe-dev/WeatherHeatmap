"""
Django admin configuration for weather models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Location, WeatherData, WeatherForecast, WeatherAlert


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'latitude', 'longitude', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['name', 'city', 'country']
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'city', 'country', 'timezone')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['location', 'condition_badge', 'temperature', 'humidity', 'wind_speed', 'timestamp', 'is_current']
    list_filter = ['condition', 'is_current', 'timestamp', 'location']
    search_fields = ['location__name', 'condition']
    readonly_fields = ['timestamp', 'raw_data']
    fieldsets = (
        ('Location & Time', {
            'fields': ('location', 'timestamp', 'is_current')
        }),
        ('Temperature', {
            'fields': ('temperature', 'feels_like', 'temp_min', 'temp_max')
        }),
        ('Atmospheric Conditions', {
            'fields': ('humidity', 'pressure', 'cloudiness', 'visibility')
        }),
        ('Wind', {
            'fields': ('wind_speed', 'wind_direction')
        }),
        ('Precipitation', {
            'fields': ('precipitation', 'condition', 'condition_description')
        }),
        ('Additional Data', {
            'fields': ('uv_index', 'api_source', 'raw_data'),
            'classes': ('collapse',)
        }),
    )
    
    def condition_badge(self, obj):
        colors = {
            'clear': '#4CAF50',
            'cloudy': '#9E9E9E',
            'rainy': '#2196F3',
            'snowy': '#E3F2FD',
            'stormy': '#F44336',
            'foggy': '#BDBDBD',
        }
        color = colors.get(obj.condition, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.condition.upper()
        )
    condition_badge.short_description = 'Condition'


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ['location', 'forecast_time', 'temperature', 'condition', 'precipitation_probability', 'created_at']
    list_filter = ['condition', 'forecast_time', 'location']
    search_fields = ['location__name']
    readonly_fields = ['created_at', 'raw_data']
    fieldsets = (
        ('Location & Time', {
            'fields': ('location', 'forecast_time', 'created_at')
        }),
        ('Temperature', {
            'fields': ('temperature', 'temp_min', 'temp_max')
        }),
        ('Conditions', {
            'fields': ('condition', 'condition_description', 'humidity', 'cloudiness')
        }),
        ('Precipitation & Wind', {
            'fields': ('precipitation', 'precipitation_probability', 'wind_speed', 'wind_direction')
        }),
        ('Additional Data', {
            'fields': ('pressure', 'api_source', 'raw_data'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'location', 'severity_badge', 'is_current_badge', 'start_time', 'end_time']
    list_filter = ['severity', 'is_active', 'alert_type', 'location']
    search_fields = ['location__name', 'alert_type', 'description']
    fieldsets = (
        ('Alert Information', {
            'fields': ('location', 'alert_type', 'severity', 'is_active')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
    
    def severity_badge(self, obj):
        colors = {
            'info': '#2196F3',
            'warning': '#FF9800',
            'critical': '#F44336',
        }
        color = colors.get(obj.severity, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.severity.upper()
        )
    severity_badge.short_description = 'Severity'
    
    def is_current_badge(self, obj):
        is_current = obj.is_current
        color = '#4CAF50' if is_current else '#757575'
        status_text = 'Active' if is_current else 'Expired'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            status_text
        )
    is_current_badge.short_description = 'Status'
