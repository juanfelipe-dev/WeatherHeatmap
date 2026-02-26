"""
Views for weather application.
"""

import json
import logging
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from .models import Location, WeatherData, WeatherForecast, WeatherAlert
from .services import WeatherService

logger = logging.getLogger(__name__)


# Serializers
class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude', 'city', 'country', 'timezone', 'is_active']


class WeatherDataSerializer(ModelSerializer):
    class Meta:
        model = WeatherData
        fields = [
            'id', 'location', 'timestamp', 'temperature', 'feels_like',
            'humidity', 'pressure', 'wind_speed', 'condition',
            'condition_description', 'precipitation', 'cloudiness'
        ]


class WeatherForecastSerializer(ModelSerializer):
    class Meta:
        model = WeatherForecast
        fields = [
            'id', 'location', 'forecast_time', 'temperature',
            'condition', 'humidity', 'wind_speed',
            'precipitation_probability', 'cloudiness'
        ]


class WeatherAlertSerializer(ModelSerializer):
    class Meta:
        model = WeatherAlert
        fields = ['id', 'location', 'alert_type', 'severity', 'description', 'start_time', 'end_time', 'is_active']


# ViewSets for API
class LocationViewSet(viewsets.ModelViewSet):
    """API ViewSet for Location management."""
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    
    @action(detail=True, methods=['get'])
    def current_weather(self, request, pk=None):
        """Get current weather for a location."""
        location = self.get_object()
        service = WeatherService()
        weather_summary = service.get_weather_summary(location)
        
        if not weather_summary:
            return Response(
                {'error': 'No current weather data available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(weather_summary)
    
    @action(detail=True, methods=['get'])
    def forecast(self, request, pk=None):
        """Get weather forecast for a location."""
        location = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        
        service = WeatherService()
        forecast_data = service.get_forecast_summary(location, hours=hours)
        
        return Response({'location': location.name, 'forecast': forecast_data})
    
    @action(detail=True, methods=['post'])
    def update_weather(self, request, pk=None):
        """Manually update weather data for a location."""
        location = self.get_object()
        service = WeatherService()
        
        try:
            weather = service.update_current_weather(location)
            forecast = service.update_forecast(location)
            
            return Response({
                'status': 'success',
                'weather_updated': weather is not None,
                'forecast_count': len(forecast)
            })
        except Exception as e:
            logger.error(f"Error updating weather: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WeatherDataViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for weather data (read-only)."""
    serializer_class = WeatherDataSerializer
    
    def get_queryset(self):
        location_id = self.request.query_params.get('location')
        queryset = WeatherData.objects.all()
        
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        return queryset.order_by('-timestamp')


class WeatherForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for weather forecasts (read-only)."""
    serializer_class = WeatherForecastSerializer
    
    def get_queryset(self):
        location_id = self.request.query_params.get('location')
        queryset = WeatherForecast.objects.filter(
            forecast_time__gte=timezone.now()
        )
        
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        return queryset.order_by('forecast_time')


class WeatherAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for weather alerts (read-only)."""
    serializer_class = WeatherAlertSerializer
    
    def get_queryset(self):
        location_id = self.request.query_params.get('location')
        queryset = WeatherAlert.objects.filter(is_active=True)
        
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        return queryset.order_by('-created_at')


# Hard-coded US cities for the weather map  
US_CITIES = [
    {"name": "New York, NY", "latitude": 40.7128, "longitude": -74.0060, "country": "United States"},
    {"name": "Los Angeles, CA", "latitude": 34.0522, "longitude": -118.2437, "country": "United States"},
    {"name": "Chicago, IL", "latitude": 41.8781, "longitude": -87.6298, "country": "United States"},
    {"name": "Houston, TX", "latitude": 29.7604, "longitude": -95.3698, "country": "United States"},
    {"name": "Phoenix, AZ", "latitude": 33.4484, "longitude": -112.0742, "country": "United States"},
    {"name": "Philadelphia, PA", "latitude": 39.9526, "longitude": -75.1652, "country": "United States"},
    {"name": "San Antonio, TX", "latitude": 29.4241, "longitude": -98.4936, "country": "United States"},
    {"name": "San Diego, CA", "latitude": 32.7157, "longitude": -117.1611, "country": "United States"},
    {"name": "Dallas, TX", "latitude": 32.7767, "longitude": -96.7970, "country": "United States"},
    {"name": "San Jose, CA", "latitude": 37.3382, "longitude": -121.8863, "country": "United States"},
    {"name": "Austin, TX", "latitude": 30.2672, "longitude": -97.7431, "country": "United States"},
    {"name": "Jacksonville, FL", "latitude": 30.3322, "longitude": -81.6557, "country": "United States"},
    {"name": "Fort Worth, TX", "latitude": 32.7555, "longitude": -97.3308, "country": "United States"},
    {"name": "Columbus, OH", "latitude": 39.9612, "longitude": -82.9988, "country": "United States"},
    {"name": "Indianapolis, IN", "latitude": 39.7684, "longitude": -86.1581, "country": "United States"},
    {"name": "Charlotte, NC", "latitude": 35.2271, "longitude": -80.8431, "country": "United States"},
    {"name": "Seattle, WA", "latitude": 47.6062, "longitude": -122.3321, "country": "United States"},
    {"name": "Denver, CO", "latitude": 39.7392, "longitude": -104.9903, "country": "United States"},
    {"name": "Washington, DC", "latitude": 38.9072, "longitude": -77.0369, "country": "United States"},
    {"name": "Boston, MA", "latitude": 42.3601, "longitude": -71.0589, "country": "United States"},
]


def index(request):
    """Overview page with cards and statistics (dashboard alternative)."""
    locations = Location.objects.filter(is_active=True)
    
    # Get current weather for all locations
    current_weather = {}
    for location in locations:
        weather = location.weather_data.filter(is_current=True).first()
        if weather:
            current_weather[location.id] = {
                'temperature': weather.temperature,
                'condition': weather.condition,
                'humidity': weather.humidity,
            }
    
    context = {
        'locations': locations,
        'current_weather': json.dumps(current_weather),
    }
    
    return render(request, 'weather/index.html', context)


def weather_map(request):
    """Dashboard map view driven by a hard-coded list of cities and live API data."""
    from django.conf import settings
    
    # Log API key status for debugging
    has_api_key = bool(settings.WEATHER_API_KEY)
    logger.info(f"weather_map: WEATHER_API_KEY present={has_api_key}")
    
    # Use mock/placeholder data for fast rendering - real data can be fetched via AJAX
    features = []
    alerts = []

    for city in US_CITIES:
        # Use placeholder data for immediate rendering
        props = {
            'name': city['name'],
            'country': city.get('country', ''),
            'temperature': 20 + (hash(city['name']) % 20 - 10),  # Pseudo-random temp 10-30°C
            'feels_like': 19,
            'condition': 'clear',
            'condition_description': 'loading...',
            'humidity': 60,
            'pressure': 1013,
            'wind_speed': 5,
            'cloudiness': 20,
            'timestamp': datetime.now().isoformat(),
            'color': '#FFD700',  # Gold for placeholder
            'icon': '🔄',  # Loading indicator
        }
        
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [city['longitude'], city['latitude']],
            },
            'properties': props,
        })

    geojson_data = {
        'type': 'FeatureCollection',
        'features': features,
    }

    context = {
        'geojson_data': json.dumps(geojson_data),
        'alerts': alerts,
        'arcgis_api_key': settings.ARCGIS_API_KEY,
    }
    return render(request, 'weather/weather_map.html', context)


@require_http_methods(["GET", "POST"])
@csrf_exempt
def api_weather_data(request):
    """API endpoint for weather data."""
    if request.method == 'GET':
        location_id = request.GET.get('location_id')
        
        if location_id:
            weather = WeatherData.objects.filter(
                location_id=location_id,
                is_current=True
            ).first()
        else:
            weather = WeatherData.objects.filter(is_current=True)
        
        if weather:
            if isinstance(weather, WeatherData):
                data = {
                    'location': weather.location.name,
                    'temperature': weather.temperature,
                    'condition': weather.condition,
                    'humidity': weather.humidity,
                    'wind_speed': weather.wind_speed,
                }
            else:
                data = [
                    {
                        'location_id': w.location.id,
                        'location': w.location.name,
                        'temperature': w.temperature,
                        'condition': w.condition,
                        'humidity': w.humidity,
                    }
                    for w in weather
                ]
            
            return JsonResponse({'success': True, 'data': data})
        
        return JsonResponse({'success': False, 'error': 'No weather data found'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_http_methods(["GET"])
def heatmap_data(request):
    """Get heatmap data for temperature visualization."""
    weather_data = WeatherData.objects.filter(is_current=True).select_related('location')
    
    heatmap_points = [
        {
            'lat': w.location.latitude,
            'lng': w.location.longitude,
            'value': w.temperature,
            'location': w.location.name,
            'condition': w.condition,
        }
        for w in weather_data
    ]
    
    return JsonResponse({
        'success': True,
        'data': heatmap_points
    })


def get_temperature_color(temp):
    """Get color based on temperature."""
    if temp <= 0:
        return '#0000ff'  # Blue for cold
    elif temp <= 10:
        return '#00ffff'  # Cyan
    elif temp <= 20:
        return '#00ff00'  # Green
    elif temp <= 30:
        return '#ffff00'  # Yellow
    elif temp <= 40:
        return '#ff8800'  # Orange
    else:
        return '#ff0000'  # Red for hot


def get_weather_icon(condition):
    """Get icon based on weather condition."""
    icons = {
        'clear': '☀️',
        'cloudy': '☁️',
        'rainy': '🌧️',
        'snowy': '❄️',
        'stormy': '⛈️',
        'foggy': '🌫️',
    }
    return icons.get(condition, '🌤️')


# Import settings for the view
from django.conf import settings
