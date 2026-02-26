# Weather Heatmap API

A Django-based weather mapping application with real-time temperature visualization, GIS integration, and weather forecasting capabilities.

## Features

- 🌡️ **Real-time Weather Data**: Fetch current weather conditions from OpenWeatherMap API
- 📍 **Geographic Visualization**: Interactive Leaflet.js maps with weather data overlays
- 🔥 **Heatmap Display**: Temperature visualization across multiple locations
- 📊 **Weather Forecasts**: 5-day forecast data for all monitored locations
- ⚠️ **Weather Alerts**: Create and manage critical weather warnings
- 🌐 **REST API**: Comprehensive API endpoints for programmatic access
- 📱 **Responsive Design**: Mobile-friendly interface with Bootstrap
- 🔄 **Auto-Refresh**: Automatic weather data updates at configurable intervals
- 🏢 **Admin Panel**: Django admin interface for complete data management
- 🛠️ **GIS Integration**: Ready for ArcGIS and spatial data operations

## Technology Stack

- **Backend**: Python 3.10+, Django 4.2+
- **API**: Django REST Framework
- **Frontend**: HTML5, Bootstrap 5, JavaScript (Vanilla)
- **Mapping**: Leaflet.js, Heatmap.js
- **External APIs**: OpenWeatherMap, ArcGIS
- **Database**: SQLite (dev), PostgreSQL (production)
- **Server**: Nginx, Gunicorn

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or conda
- Virtual environment (recommended)

### Setup Steps

1. **Clone and Navigate**
   ```bash
   cd "f:\Copilot Projects\Heatmap"
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

5. **Initialize Database**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

Visit http://localhost:8000 in your browser.

## Configuration

### OpenWeatherMap API

1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Add to `.env`:
   ```
   WEATHER_API_KEY=your_api_key_here
   ```

### ArcGIS Integration (Optional)

1. Create an ArcGIS Developer account at https://developers.arcgis.com
2. Generate an API key
3. Add to `.env`:
   ```
   ARCGIS_API_KEY=your_arcgis_key_here
   ```

## Usage

### Web Interface

- **Dashboard** (`/`): Interactive map with real‑time heatmap and sidebar cards (beautiful, responsive layout). The map automatically zooms into U.S. locations if any are configured, otherwise it fits all points.
- **Overview** (`/overview/`): Grid of individual weather cards with statistics and quick navigation
- **Admin Panel** (`/admin/`): Manage locations, weather data, and alerts

### API Endpoints

All endpoints require the `/api/` prefix.

#### Locations
```
GET    /api/locations/                    # List all locations
GET    /api/locations/{id}/               # Get specific location
POST   /api/locations/                    # Create location
PUT    /api/locations/{id}/               # Update location
DELETE /api/locations/{id}/               # Delete location
```

#### Weather Data
```
GET /api/locations/{id}/current_weather/  # Get current weather
GET /api/locations/{id}/forecast/         # Get 5-day forecast
POST /api/locations/{id}/update_weather/  # Manually update weather
```

#### Forecasts
```
GET /api/forecasts/                       # List all forecasts
GET /api/forecasts/?location={id}         # Filter by location
```

#### Alerts
```
GET /api/alerts/                          # List active alerts
GET /api/alerts/?location={id}            # Get alerts for location
```

### Management Commands

```bash
# Update weather for all locations
python manage.py fetch_weather

# Update specific location
python manage.py fetch_weather --location-id=1

# Verbose output
python manage.py fetch_weather --verbose

# Forecast only
python manage.py fetch_weather --forecast-only
```

## Database Models

### Location
Stores geographic information for monitored locations.

```python
- name (CharField): Unique location name
- latitude (FloatField): Geographic latitude
- longitude (FloatField): Geographic longitude
- city, country, timezone (CharField): Location metadata
- is_active (BooleanField): Active status
```

### WeatherData
Current and historical weather information.

```python
- location (ForeignKey): Associated location
- temperature (FloatField): Current temperature in Celsius
- humidity (IntegerField): Humidity percentage
- pressure (IntegerField): Atmospheric pressure
- wind_speed (FloatField): Wind speed in m/s
- condition (CharField): Weather condition (clear, cloudy, rainy, etc.)
- timestamp (DateTimeField): Data timestamp
- is_current (BooleanField): Flag for most recent data
```

### WeatherForecast
Predicted weather for future time periods.

```python
- location (ForeignKey): Associated location
- forecast_time (DateTimeField): Time forecast is for
- temperature, humidity, wind_speed (FloatField)
- condition (CharField): Predicted condition
- precipitation_probability (IntegerField): Chance of rain
```

### WeatherAlert
Critical weather warnings and alerts.

```python
- location (ForeignKey): Affected location
- alert_type (CharField): Alert type (Heat Wave, Frost Warning, etc.)
- severity (CharField): Alert severity (info, warning, critical)
- description (TextField): Alert details
- start_time, end_time (DateTimeField): Alert period
- is_active (BooleanField): Current status
```

## Frontend Components

### Weather Cards
Display current conditions with temperature, humidity, wind speed, and forecast.

### Interactive Map
- Leaflet.js-powered mapping
- GeoJSON data visualization
- Responsive zoom and pan
- Location markers with weather popups

### Temperature Heatmap
- Color-coded temperature visualization
- 6-point temperature scale (blue to red)
- Automatic scaling based on data range

### Responsive Design
- Mobile-friendly layout
- Touch-friendly controls
- Bootstrap grid system
- CSS Grid for weather details

## Development

### Project Structure

```
heatmap_project/
├── settings.py          # Django configuration
├── urls.py              # URL routing
├── wsgi.py              # WSGI application
└── __init__.py

weather/
├── models.py            # Database models
├── views.py             # View logic
├── services.py          # API clients and business logic
├── urls.py              # App URL routing
├── admin.py             # Admin configuration
├── forms.py             # Django forms
├── signals.py           # Django signals
├── management/
│   └── commands/
│       └── fetch_weather.py  # Weather update command
├── templates/weather/
│   ├── base.html        # Base template
│   ├── index.html       # Overview page (grid of weather cards)
│   └── weather_map.html # Dashboard map page
└── static/weather/
    ├── ui.css           # Stylesheets
    └── ui.js            # JavaScript
```

### Adding a New Location

Via Admin:
1. Go to http://localhost:8000/admin/
2. Click "Locations" → "Add location"
3. Fill in name, coordinates, city, country
4. Save

Via API:
```bash
curl -X POST http://localhost:8000/api/locations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New York",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "city": "New York",
    "country": "United States"
  }'
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in settings
- [ ] Update `SECRET_KEY` to a secure random value
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up SSL/TLS certificates
- [ ] Configure Nginx reverse proxy
- [ ] Use Gunicorn as WSGI server
- [ ] Set up Celery for async tasks
- [ ] Configure logging and monitoring
- [ ] Set up automated backups

### Nginx Configuration

Reference deployment files in `deploy/nginx/` for example Nginx configuration.

### Systemd Service

Reference files in `deploy/systemd/` for example systemd service configuration.

## Troubleshooting

### Weather API Key Not Working
- Verify API key in `.env` file
- Check OpenWeatherMap API usage limits
- Ensure key is for the correct API endpoint

### Map Not Displaying
- Check browser console for JavaScript errors
- Verify Leaflet.js CDN is accessible
- Check GeoJSON data format

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database Errors
```bash
python manage.py migrate
python manage.py migrate --run-syncdb
```

## Performance Optimization

### Database Indexing
Models include optimized indexes for common queries.

### Caching
Implement Redis caching for weather data:
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # 5 minutes
def weather_data_view(request):
    ...
```

### API Rate Limiting
Consider using `django-ratelimit` for API endpoints.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Check existing documentation
- Review API documentation at `/api/`

## Changelog

### Version 1.0.0 (2026-02-25)
- Initial release
- OpenWeatherMap integration
- Interactive map visualization
- REST API endpoints
- Django admin interface
- Management commands for data updates

## Future Features

- [ ] Real-time WebSocket updates
- [ ] Advanced analytics and reporting
- [ ] Multiple weather API providers
- [ ] Machine learning predictions
- [ ] Mobile app (React Native/Flutter)
- [ ] SMS/Email alerts
- [ ] Historical data analysis
- [ ] Custom data visualizations

---

Built with ❤️ for weather enthusiasts and GIS professionals
