# Deploying to Render.com

This guide will help you deploy the Weather Heatmap project to Render.com.

## Prerequisites

- Render.com account (free tier available)
- GitHub repository with your code pushed
- OpenWeatherMap API key (optional but recommended)
- ArcGIS API key (optional)

## Step-by-Step Deployment

### 1. Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Fill in the details:
   - **Name**: `weather-heatmap-db` (or your choice)
   - **Database**: `heatmap_db`
   - **User**: `heatmap_user`
   - **Region**: Choose closest to your users
   - **Version**: Latest PostgreSQL
4. Click **Create Database**
5. Copy the **Database URL** right away (you'll need it)

### 2. Create Web Service on Render

1. Click **New +** → **Web Service**
2. Select your GitHub repository (or connect if needed)
3. Fill in the service details:
   - **Name**: `weather-heatmap`
   - **Region**: Same as your database
   - **Branch**: `main` (or your main branch)
   - **Runtime**: `Python 3.11`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command**:
     ```bash
     gunicorn heatmap_project.wsgi:application
     ```

### 3. Set Environment Variables

In the **Environment** section, add these variables:

| Key | Value |
|-----|-------|
| `DJANGO_SECRET_KEY` | Generate a random string (use a [Django secret key generator](https://djecrety.ir/)) |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | Your Render domain (e.g., `weather-heatmap.onrender.com`) |
| `DATABASE_URL` | Paste the PostgreSQL URL from step 1 |
| `WEATHER_API_KEY` | Your OpenWeatherMap API key (optional) |
| `ARCGIS_API_KEY` | Your ArcGIS API key (optional) |
| `PYTHON_VERSION` | `3.11.0` |

### 4. Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run migrations
   - Collect static files
   - Start your app with Gunicorn

## What the Build Command Does

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

1. **`pip install -r requirements.txt`** - Installs all Python packages
2. **`python manage.py migrate`** - Creates database tables
3. **`python manage.py collectstatic --noinput`** - Collects static files (CSS, JS, images)

## Important Configuration

- ✅ **WhiteNoise** is configured to serve static files efficiently
- ✅ **CORS** settings allow `onrender.com` domains
- ✅ **Database** defaults to PostgreSQL when `DATABASE_URL` is set
- ✅ **SQLite** works locally (development)
- ✅ **Gunicorn** is configured for production

## Auto-Deploy on Push

Your app will automatically redeploy when you push to your GitHub main branch (disable this in service settings if needed).

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version is 3.11

### Database Connection Issues
- Double-check `DATABASE_URL` is correct
- Ensure database is fully provisioned (wait a few minutes)
- Check Django debug logs: add `-v 2` to your manage.py command for more details

### Static Files Not Loading
- WhiteNoise should handle this automatically
- If not, run: `python manage.py collectstatic --noinput`

### App Crashes on Startup
- Check logs for database migration errors
- Ensure `DJANGO_SECRET_KEY` is set
- Verify `DJANGO_ALLOWED_HOSTS` includes your Render domain

## Database Backup

Render's managed PostgreSQL includes:
- Automatic daily backups
- Point-in-time recovery available
- No action needed on your part

## Cost

On Render's free tier:
- Web service: Free
- PostgreSQL database: Free (limited storage)
- Spinning down after 15 minutes of inactivity: Auto-applied

To keep your service always running, upgrade to a paid plan.

## Next Steps

1. Monitor your deployment in the Render dashboard
2. Check logs if there are any issues
3. Set up your API keys for full functionality
4. Consider upgrading to a paid plan for production use

For more help, check [Render's Django documentation](https://render.com/docs/deploy-django).
