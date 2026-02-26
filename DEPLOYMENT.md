# Deployment to Render.com

This guide walks you through deploying the Weather Heatmap to [Render.com](https://render.com).

## Prerequisites

- GitHub account with the project repository pushed
- Render.com account (sign up at https://render.com)
- Environment variables ready (API keys, etc.)

## Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: weather heatmap MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/heatmap.git
git push -u origin main
```

## Step 2: Create Render Account & Connect GitHub

1. Go to https://render.com and sign up
2. Click **Dashboard** → **New +** → **Web Service**
3. Select "Build and deploy from a Git repository"
4. Connect your GitHub account and select this repository
5. Click **Connect**

## Step 3: Configure the Web Service

In the Render deployment form, fill in:

| Field | Value |
|-------|-------|
| **Name** | `heatmap-api` (or any name) |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (or closest to you) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput` |
| **Start Command** | `gunicorn heatmap_project.wsgi:application --bind 0.0.0.0:$PORT` |
| **Plan** | `Free` (or paid if you prefer) |

Click **Create Web Service**

## Step 4: Add Environment Variables

After the service is created, go to **Settings** → **Environment** and add:

```
DJANGO_SECRET_KEY=your-secret-key-here
WEATHER_API_KEY=your-openweathermap-key
ARCGIS_API_KEY=your-arcgis-key (optional)
DJANGO_DEBUG=False
ALLOWED_HOSTS=*.onrender.com
DATABASE_URL=(auto-populated if using Render Postgres)
```

### Generate a New SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it into `DJANGO_SECRET_KEY`.

## Step 5: Add a PostgreSQL Database (Optional but Recommended)

For production, use PostgreSQL instead of SQLite:

1. In Render dashboard, click **New +** → **PostgreSQL**
2. Set **Name** to `heatmap-db`
3. Set **Database** to `heatmap`
4. Keep **Region** the same as your web service
5. Click **Create**
6. Render will automatically populate `DATABASE_URL` in your web service

If you use the included `render.yaml`, the database will be created automatically.

## Step 6: Deploy

Once configured, Render will automatically:
1. Install dependencies from `requirements.txt`
2. Collect static files
3. Run database migrations
4. Start the Gunicorn server

Monitor the build log in the **Deploys** tab. When status shows **Live**, your app is ready!

## Step 7: Access Your App

Your app will be live at: `https://heatmap-api.onrender.com` (or the URL shown in Render)

Navigate to:
- **Dashboard**: `https://heatmap-api.onrender.com/`
- **Overview**: `https://heatmap-api.onrender.com/overview/`
- **API**: `https://heatmap-api.onrender.com/api/`
- **Admin**: `https://heatmap-api.onrender.com/admin/`

## Step 8: Create Admin User (First Time Only)

After deployment, create a superuser:

1. Go to your service's **Shell** tab in Render
2. Run:
   ```bash
   python manage.py createsuperuser
   ```
3. Follow prompts to create admin account
4. Log in at `/admin/` with those credentials

## Step 9: Load Sample Data

In the Shell, run:

```bash
python manage.py load_sample_locations --clear
python manage.py fetch_weather --verbose
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'rest_framework'"
- Ensure `requirements.txt` has `djangorestframework`
- Redeploy with **Manual Deploy** button

### "Static files not loading"
- Check that `STATIC_ROOT` is set in `settings.py`
- Ensure `collectstatic` ran successfully in build log
- For custom static URLs, check Render's static file serving

### Database migration errors
- Check **Logs** → **Build Log** for SQL errors
- Manually run migrations in Shell:
  ```bash
  python manage.py migrate
  ```

### 500 errors after deployment
- Check **Logs** for error messages
- Ensure all environment variables are set correctly
- Test locally with `DEBUG=True` (temporarily, never in production)

## Using render.yaml (Alternative)

Instead of manual configuration, you can use the included `render.yaml`:

1. Push `render.yaml` to GitHub
2. In Render, click **New +** → **Infrastructure as Code**
3. Select your repo
4. Render will read `render.yaml` and auto-configure everything

This is recommended for reproducible deployments.

## Updating Your App

Every time you push to `main`:

```bash
git add .
git commit -m "Update: [your changes]"
git push origin main
```

Render automatically rebuilds and redeploys. Monitor in the **Deploys** tab.

## Free Tier Limits (Render)

- **Spin down after 15 minutes of inactivity** (app goes to sleep)
- **Rebuilds take ~5 minutes**
- Database restarts nightly
- Limited compute/RAM

Upgrade to a paid plan for always-on service and better performance.

## Next Steps

- Set up a custom domain (Render → **Settings** → **Custom Domain**)
- Configure monitoring and alerts
- Set up automatic backups for PostgreSQL
- Add a cron job to refresh weather data (via scheduled tasks)

---

Questions? Check [Render Docs](https://render.com/docs) or reach out to support.
