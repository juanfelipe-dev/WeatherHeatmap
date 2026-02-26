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
from .models import WeatherData, WeatherForecast, WeatherAlert, Location  # importing Location for potential use (index view/API)

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


# Template Views

# import full city list from management command to avoid duplication
from weather.management.commands.load_us_cities import US_CITIES as _LOAD_CITIES

US_CITIES = [
    {
        "name": f"{city}, {state_code}",
        "latitude": lat,
        "longitude": lon,
        "country": "United States",
    }
    for city, lat, lon, state_code, state_name in _LOAD_CITIES
]

def index(request):
    """Overview page with cards and statistics (dashboard alternative)."""
    # optionally read locations from DB, but ignore errors if database missing
    locations = []
    current_weather = {}
    try:
        locations = Location.objects.filter(is_active=True)
        for location in locations:
            weather = location.weather_data.filter(is_current=True).first()
            if weather:
                current_weather[location.id] = {
                    'temperature': weather.temperature,
                    'condition': weather.condition,
                    'humidity': weather.humidity,
                }
    except Exception:
        # database might not exist or be inaccessible; just show empty lists
        locations = []
        current_weather = {}

    context = {
        'locations': locations,
        'current_weather': json.dumps(current_weather),
    }

    return render(request, 'weather/index.html', context)


def weather_map(request):
    """Dashboard map view driven by a hard-coded list of cities and live API data."""
    service = WeatherService()
    features = []

    # no database alerts when hard-coding locations
    alerts = []

    for city in US_CITIES:
        raw = service.client.fetch_current_weather(city['latitude'], city['longitude'])
        if not raw:
            continue
        main = raw.get('main', {})
        weather_info = raw.get('weather', [{}])[0]
        temp = main.get('temp')
        props = {
            'name': city['name'],
            'country': city.get('country', ''),
            'temperature': temp,
            'feels_like': main.get('feels_like'),
            'condition': weather_info.get('main', '').lower(),
            'condition_description': weather_info.get('description', ''),
            'humidity': main.get('humidity'),
            'pressure': main.get('pressure'),
            'wind_speed': raw.get('wind', {}).get('speed'),
            'cloudiness': raw.get('clouds', {}).get('all'),
            'timestamp': datetime.utcfromtimestamp(raw.get('dt', 0)).isoformat(),
            'color': get_temperature_color(temp) if temp is not None else '#888',
            'icon': get_weather_icon(weather_info.get('main', '').lower()),
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
