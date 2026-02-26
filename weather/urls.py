"""
URL configuration for weather app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'weather', views.WeatherDataViewSet, basename='weather-data')
router.register(r'forecasts', views.WeatherForecastViewSet, basename='forecast')
router.register(r'alerts', views.WeatherAlertViewSet, basename='alert')

app_name = 'weather'

urlpatterns = [
    # API endpoints under /api/
    path('api/', include(router.urls)),

    # Template views
    path('', views.weather_map, name='dashboard'),  # homepage shows map dashboard
    path('overview/', views.index, name='overview'),

    # Data endpoints (for legacy/JS use if still required)
    path('api/weather-data/', views.api_weather_data, name='api-weather-data'),
    path('api/heatmap-data/', views.heatmap_data, name='heatmap-data'),
]
