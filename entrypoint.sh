#!/bin/sh
set -e

python manage.py makemigrations articles crawler --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py add_seeds --noinput
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
