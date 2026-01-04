e# NousNews Backend

Django REST API service with a dedicated Postgres database. The crawler runs inside this backend as a Django app.

## Quick start

1. Copy environment file:

```sh
cp .env.example .env
```

2. Create shared network (once per host):

```sh
docker network create nousnews
```

3. Build and run services:

```sh
docker compose up --build
```

4. The container startup runs migrations, collectstatic, and seeds automatically.

API is served at `http://localhost:8210/api/`.

Crawler control and status endpoints are restricted to private network requests (no shared token required).

## Endpoints

- `GET /api/health/`
- `GET /api/articles/`
- `GET /api/articles/{id}/`
- `POST /api/articles/ingest/` (optional, internal use)
- `GET /api/crawler/status/`
- `POST /api/crawler/run/`
- `GET /api/crawler/config/`
- `PUT /api/crawler/config/`
- `GET /api/crawler/seeds/`
- `POST /api/crawler/seeds/`
- `GET /api/crawler/export.csv`

To enable the LLM pipeline, configure provider/model/token in the admin `Crawler Configuration`.

Seed URLs are stored in the database; add them via `POST /api/crawler/seeds/` before starting a run.

## Local development (optional)

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
