"""
Weather API service - Integrates with OpenWeatherMap and other weather APIs.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from .models import WeatherData, Location, WeatherForecast, WeatherAlert

logger = logging.getLogger(__name__)


class WeatherAPIClient:
    """Base client for weather API interactions."""
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_BASE_URL
        self.timeout = 10
        
    def fetch_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Fetch current weather data from API."""
        raise NotImplementedError
    
    def fetch_forecast(self, latitude: float, longitude: float, days: int = 5) -> Optional[List[Dict]]:
        """Fetch weather forecast data from API."""
        raise NotImplementedError


class OpenWeatherMapClient(WeatherAPIClient):
    """OpenWeatherMap API client implementation."""
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        
    def fetch_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Fetch current weather from OpenWeatherMap API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dictionary with weather data or None if request fails
        """
        if not self.api_key:
            logger.warning("WEATHER_API_KEY not configured")
            return None
            
        url = f"{self.base_url}/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def fetch_forecast(self, latitude: float, longitude: float, days: int = 5) -> Optional[List[Dict]]:
        """
        Fetch 5-day weather forecast from OpenWeatherMap API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days to forecast (max 5 for free tier)
            
        Returns:
            List of forecast dictionaries or None if request fails
        """
        if not self.api_key:
            logger.warning("WEATHER_API_KEY not configured")
            return None
            
        url = f"{self.base_url}/forecast"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get('list', [])
        except requests.RequestException as e:
            logger.error(f"Error fetching forecast data: {e}")
            return None


class WeatherService:
    """Service for managing weather data operations."""
    
    def __init__(self, client: Optional[WeatherAPIClient] = None):
        self.client = client or OpenWeatherMapClient()
    
    def update_current_weather(self, location: Location) -> Optional[WeatherData]:
        """
        Update current weather for a location.
        
        Args:
            location: Location object to update
            
        Returns:
            Updated WeatherData object or None if update fails
        """
        raw_data = self.client.fetch_current_weather(location.latitude, location.longitude)
        
        if not raw_data:
            return None
        
        try:
            weather = self._parse_current_weather(raw_data, location)
            weather.is_current = True
            weather.raw_data = raw_data
            weather.api_source = 'openweathermap'
            weather.save()
            
            # Mark previous weather as non-current
            WeatherData.objects.filter(
                location=location,
                is_current=True
            ).exclude(id=weather.id).update(is_current=False)
            
            logger.info(f"Updated weather for {location.name}")
            return weather
        except Exception as e:
            logger.error(f"Error parsing weather data for {location.name}: {e}")
            return None
    
    def update_forecast(self, location: Location) -> List[WeatherForecast]:
        """
        Update weather forecast for a location.
        
        Args:
            location: Location object to update
            
        Returns:
            List of created/updated WeatherForecast objects
        """
        forecast_data = self.client.fetch_forecast(location.latitude, location.longitude)
        
        if not forecast_data:
            return []
        
        forecasts = []
        try:
            for item in forecast_data[:40]:  # 5 days * 8 (3-hourly data)
                forecast = self._parse_forecast_item(item, location)
                forecast.raw_data = item
                forecast.api_source = 'openweathermap'
                forecast.save()
                forecasts.append(forecast)
            
            logger.info(f"Updated {len(forecasts)} forecast records for {location.name}")
            return forecasts
        except Exception as e:
            logger.error(f"Error parsing forecast data for {location.name}: {e}")
            return forecasts
    
    def _parse_current_weather(self, data: Dict, location: Location) -> WeatherData:
        """Parse OpenWeatherMap current weather response."""
        condition_map = {
            'Clear': 'clear',
            'Clouds': 'cloudy',
            'Rain': 'rainy',
            'Snow': 'snowy',
            'Thunderstorm': 'stormy',
            'Mist': 'foggy',
            'Smoke': 'foggy',
            'Haze': 'foggy',
            'Dust': 'foggy',
            'Fog': 'foggy',
            'Sand': 'foggy',
            'Ash': 'foggy',
            'Squall': 'stormy',
            'Tornado': 'stormy',
            'Drizzle': 'rainy',
        }
        
        main_condition = data.get('weather', [{}])[0].get('main', 'unknown')
        condition = condition_map.get(main_condition, 'unknown')
        
        return WeatherData(
            location=location,
            temperature=data.get('main', {}).get('temp', 0),
            feels_like=data.get('main', {}).get('feels_like'),
            temp_min=data.get('main', {}).get('temp_min'),
            temp_max=data.get('main', {}).get('temp_max'),
            humidity=data.get('main', {}).get('humidity', 0),
            pressure=data.get('main', {}).get('pressure', 0),
            wind_speed=data.get('wind', {}).get('speed', 0),
            wind_direction=data.get('wind', {}).get('deg'),
            precipitation=data.get('rain', {}).get('1h', 0),
            cloudiness=data.get('clouds', {}).get('all', 0),
            visibility=data.get('visibility'),
            condition=condition,
            condition_description=data.get('weather', [{}])[0].get('description', ''),
        )
    
    def _parse_forecast_item(self, item: Dict, location: Location) -> WeatherForecast:
        """Parse OpenWeatherMap forecast item."""
        condition_map = {
            'Clear': 'clear',
            'Clouds': 'cloudy',
            'Rain': 'rainy',
            'Snow': 'snowy',
            'Thunderstorm': 'stormy',
            'Mist': 'foggy',
            'Smoke': 'foggy',
            'Haze': 'foggy',
            'Dust': 'foggy',
            'Fog': 'foggy',
            'Sand': 'foggy',
            'Ash': 'foggy',
            'Squall': 'stormy',
            'Tornado': 'stormy',
            'Drizzle': 'rainy',
        }
        
        dt = item.get('dt', 0)
        forecast_time = datetime.fromtimestamp(dt, tz=timezone.utc)
        
        main_condition = item.get('weather', [{}])[0].get('main', 'unknown')
        condition = condition_map.get(main_condition, 'unknown')
        
        return WeatherForecast(
            location=location,
            forecast_time=forecast_time,
            temperature=item.get('main', {}).get('temp', 0),
            temp_min=item.get('main', {}).get('temp_min'),
            temp_max=item.get('main', {}).get('temp_max'),
            humidity=item.get('main', {}).get('humidity', 0),
            pressure=item.get('main', {}).get('pressure', 0),
            wind_speed=item.get('wind', {}).get('speed', 0),
            wind_direction=item.get('wind', {}).get('deg'),
            precipitation=item.get('rain', {}).get('3h', 0),
            precipitation_probability=int(item.get('pop', 0) * 100),
            cloudiness=item.get('clouds', {}).get('all', 0),
            condition=condition,
            condition_description=item.get('weather', [{}])[0].get('description', ''),
        )
    
    def get_weather_summary(self, location: Location) -> Optional[Dict]:
        """Get current weather summary for a location."""
        try:
            weather = WeatherData.objects.filter(
                location=location,
                is_current=True
            ).first()
            
            if not weather:
                return None
            
            return {
                'location': location.name,
                'temperature': weather.temperature,
                'temperature_f': weather.temperature_fahrenheit,
                'condition': weather.condition,
                'description': weather.condition_description,
                'humidity': weather.humidity,
                'wind_speed': weather.wind_speed,
                'wind_speed_kmh': weather.wind_speed_kmh,
                'feels_like': weather.feels_like,
                'pressure': weather.pressure,
                'visibility': weather.visibility,
                'cloudiness': weather.cloudiness,
                'uv_index': weather.uv_index,
                'timestamp': weather.timestamp.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting weather summary for {location.name}: {e}")
            return None
    
    def get_forecast_summary(self, location: Location, hours: int = 24) -> List[Dict]:
        """Get forecast summary for next N hours."""
        try:
            cutoff_time = timezone.now() + timedelta(hours=hours)
            forecasts = WeatherForecast.objects.filter(
                location=location,
                forecast_time__gte=timezone.now(),
                forecast_time__lte=cutoff_time
            ).order_by('forecast_time')
            
            return [
                {
                    'time': f.forecast_time.isoformat(),
                    'temperature': f.temperature,
                    'condition': f.condition,
                    'wind_speed': f.wind_speed,
                    'precipitation_probability': f.precipitation_probability,
                    'humidity': f.humidity,
                }
                for f in forecasts
            ]
        except Exception as e:
            logger.error(f"Error getting forecast summary for {location.name}: {e}")
            return []
