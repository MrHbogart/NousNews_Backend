#!/bin/sh
set -e

python - <<'PY'
import os
import time
import psycopg

host = os.getenv("DJANGO_DB_HOST", "db")
port = int(os.getenv("DJANGO_DB_PORT", "5432"))
name = os.getenv("DJANGO_DB_NAME", "nousnews")
user = os.getenv("DJANGO_DB_USER", "nousnews")
password = os.getenv("DJANGO_DB_PASSWORD", "nousnews")

for attempt in range(1, 31):
    try:
        with psycopg.connect(
            host=host,
            port=port,
            dbname=name,
            user=user,
            password=password,
        ):
            break
    except Exception:
        if attempt == 30:
            raise
        time.sleep(1)
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py add_seeds
python manage.py shell <<'PY'
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(email="admin@admin.com").exists():
    User.objects.create_superuser(
        username="admin",
        email="admin@admin.com",
        password="adminadmin",
    )
PY

exec "$@"
