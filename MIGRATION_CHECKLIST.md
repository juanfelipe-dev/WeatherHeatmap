# Migration & Production DB Checklist

Follow this checklist when switching to PostgreSQL or deploying to production (Render).

1. Provision a PostgreSQL database (Render managed DB or other provider).
   - Note the full `DATABASE_URL` (e.g. `postgres://user:pass@host:5432/dbname`).

2. Set environment variables in Render (Service > Environment > Environment Variables):
   - `DATABASE_URL` = your Postgres connection URL
   - `DJANGO_SECRET_KEY` = secure random string
   - `DJANGO_DEBUG` = `False`
   - `DJANGO_ALLOWED_HOSTS` = your-app.onrender.com

3. Ensure `requirements.txt` contains these packages:
   - `psycopg2-binary`
   - `dj-database-url`

4. Confirm your Render Build Command includes migrations and collectstatic:

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

5. Commit & push changes (remove `db.sqlite3` and add to `.gitignore`):

```bash
git add -A
git commit -m "Remove SQLite and switch to PostgreSQL for production"
git push
```

6. Trigger a redeploy on Render (push or manual deploy). Watch logs for:
   - `Applying ...` migration lines
   - `Collecting static files` completion
   - `Starting gunicorn` without ImportError or OperationalError

7. Verify the site:
   - Visit `https://your-app.onrender.com`
   - Check `/admin/` and any API endpoints

8. If you need initial data (superuser):
   - SSH/Run a one-off shell on your host or run locally against the same DB connection:

```bash
python manage.py createsuperuser
```

9. Backups & monitoring:
   - Enable daily backups for managed DB
   - Check logs for errors after each deploy


If anything fails, collect the Render service logs and share the error lines for targeted help.
