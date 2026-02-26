# Weather Heatmap - Quick Start Guide

Get up and running with the Weather Heatmap application in minutes!

## ✅ What You Have

The complete weather integration has been set up with:

- ✅ Django 4.2 backend with REST API
- ✅ 4 database models (Location, WeatherData, WeatherForecast, WeatherAlert)
- ✅ OpenWeatherMap API integration
- ✅ Interactive map with Leaflet.js
- ✅ Temperature heatmap visualization
- ✅ Admin panel for data management
- ✅ 10 sample locations pre-loaded (NY, London, Tokyo, Sydney, Paris, Singapore, Toronto, Dubai, São Paulo, Istanbul)

## 🚀 Quick Start (5 minutes)

### Step 1: Configure API Key (Required)

1. Get a **FREE** weather API key from: https://openweathermap.org/api

2. Create a `.env` file in the project root:
   ```bash
   copy .env.example .env
   ```

3. Edit `.env` and add your API key:
   ```
   WEATHER_API_KEY=your_api_key_here
   ```

### Step 2: Start the Server

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Start the development server
python manage.py runserver 0.0.0.0:8000
```

### Step 3: Access the Application

- 🌐 **Web Interface**: http://localhost:8000/
- 🗂️ **Admin Panel**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin123` (change this!)

## 📍 Fetch Weather Data

```bash
# Get weather for first 10 locations
python manage.py fetch_weather 

# Get weather for all active locations
python manage.py fetch_weather --all-locations

# Get weather for specific location
python manage.py fetch_weather --location-id=1

# Verbose output
python manage.py fetch_weather --verbose
```

After running this command, refresh the web interface to see the weather data!

## 🗺️ What You Can Do

### Dashboard (Map + Sidebar)
- Root URL (`/`) now shows a beautiful dashboard with an interactive map on the left
  and weather cards on the right
- Toolbar at top lets you toggle the sidebar, export data as CSV, or print the map
- Click on any marker to see details and use the sidebar list to jump to locations

### Overview
- Visit `/overview/` for a grid of cards summarizing current weather across locations
- Includes quick statistics and a button to return to the dashboard

### View Current Weather
- Each overview card shows temperature, humidity, wind speed, and condition data

### Interactive Map Features
- Color-coded markers indicate temperature ranges
- Map auto‑fits to visible locations and will start focused on the United States when U.S. locations exist
- Export, print, and sidebar-toggle buttons make the dashboard client-ready

### Manage Data
- Go to Admin panel (`/admin/`) to:
  - Add/edit/delete locations
  - View weather history
  - Create weather alerts
  - Monitor forecast data

### Use the API

```bash
# List all locations
curl http://localhost:8000/api/locations/

# Get specific location
curl http://localhost:8000/api/locations/1/

# Get current weather
curl http://localhost:8000/api/locations/1/current_weather/

# Get forecast
curl http://localhost:8000/api/locations/1/forecast/?hours=24

# Get heatmap data
curl http://localhost:8000/api/heatmap-data/
```

## 📁 Project Structure

```
heatmap_project/
├── settings.py          # Django configuration
├── urls.py              # URL routing
├── wsgi.py              # WSGI app

weather/                 # Main app
├── models.py            # Database models
├── views.py             # Views and API endpoints
├── services.py          # OpenWeatherMap integration
├── urls.py              # App URLs
├── admin.py             # Admin configuration
├── management/          # Custom commands
│   └── commands/
│       ├── fetch_weather.py
│       └── load_sample_locations.py
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   └── weather_map.html
└── static/              # CSS, JavaScript
    └── weather/
        ├── ui.css
        └── ui.js

Requirements:
├── manage.py            # Django CLI
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md            # Full documentation
```

## 🔑 Key Features

### Real-time Weather Data
- Fetches from OpenWeatherMap API
- Stores temperature, humidity, pressure, wind speed
- Automatic condition detection (clear, cloudy, rainy, etc.)

### 5-Day Forecast
- Hourly forecast data for 5 days
- Precipitation probability
- Temperature ranges

### Weather Alerts
- Create critical weather warnings
- Set severity levels (info, warning, critical)
- Active/expired status tracking

### Temperature Visualization
- Color-coded heatmap (blue to red)
- Geographic markers on interactive map
- Real-time updates

### GIS-Ready
- Geographic coordinates storage
- Designed for ArcGIS integration
- Extensible for spatial analysis

## 🔧 Configuration

### Database
Default: SQLite (file-based, no setup needed)

For PostgreSQL:
```bash
pip install psycopg2-binary
# Update DATABASE_URL in .env:
# DATABASE_URL=postgresql://user:password@localhost:5432/heatmap_db
```

### Async Tasks (Optional)
For scheduled weather updates:
```bash
pip install celery redis
python manage.py celery worker -l info
```

### Static Files (Production)
```bash
python manage.py collectstatic --noinput
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'rest_framework'"
```bash
pip install -r requirements.txt
```

### No weather data showing
1. Verify API key in `.env`
2. Run: `python manage.py fetch_weather --verbose`
3. Check OpenWeatherMap API status

### Port 8000 already in use
```bash
python manage.py runserver 0.0.0.0:8001
```

### Admin login issues
```bash
python manage.py changepassword admin
```

## 📚 Useful Commands

```bash
# Create new location
python manage.py shell
>>> from weather.models import Location
>>> Location.objects.create(
...     name="Berlin",
...     latitude=52.52,
...     longitude=13.405,
...     city="Berlin",
...     country="Germany"
... )

# Check database
python manage.py dbshell

# Run tests
python manage.py test

# Generate API documentation
python manage.py api_schema

# Clear all data
python manage.py flush --noinput

# Show available commands
python manage.py help
```

## 🚀 Next Steps

### Customize
- Edit templates in `weather/templates/`
- Modify styles in `weather/static/weather/ui.css`
- Add new API endpoints in `weather/views.py`

### Deploy
- See `deploy/` directory for Nginx, systemd, k8s configs
- Use `docker-compose.yml` for containerization
- Follow production setupin `README.md`

### Integrate
- Add authentication
- Connect to your GIS system
- Add more weather APIs
- Build mobile app

## 📖 Full Documentation

See `README.md` for:
- Detailed API documentation
- Deployment instructions
- Database schema
- Advanced features
- Contributing guidelines

## 💡 Tips

1. **API Updates**: Run `fetch_weather` periodically via cron or Celery
2. **Monitoring**: Check logs in `logs/django.log`
3. **Performance**: Use Redis for caching weather data
4. **Scaling**: PostgreSQL for production environments
5. **GIS**: Add GeoDjango for spatial queries

## 🤝 Support

- Full API documentation: `/api/`
- Django Admin Help: `/admin/`
- GitHub Issues: [Your repo]
- Email: support@example.com

## 🎉 You're Ready!

Your weather heatmap is configured and running!

```
Start server: python manage.py runserver 0.0.0.0:8000
Open browser: http://localhost:8000/
Fetch weather: python manage.py fetch_weather
View admin: http://localhost:8000/admin/
```

Happy weather mapping! 🌤️
