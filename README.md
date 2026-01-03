# NousNews Backend

Django REST API service with a dedicated Postgres database. The crawler runs as a separate service.

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

4. Apply migrations:

```sh
docker compose exec web python manage.py migrate
```

API is served at `http://localhost:8210/api/`. The crawler listens on `http://localhost:8211/`.

Set the same `CRAWLER_API_TOKEN` in the crawler `.env` as `API_TOKEN`, and in the backend `.env` as
`CRAWLER_API_TOKEN`, so commands and article ingestion are authenticated.

## Endpoints

- `GET /api/health/`
- `GET /api/articles/`
- `GET /api/articles/{id}/`
- `POST /api/articles/ingest/`
- `POST /api/crawler/command/`

Crawler commands:

```json
{ "action": "crawl" }
{ "action": "pause" }
{ "action": "resume" }
{ "action": "stop" }
{ "action": "set-delay", "value": 1.2 }
```

## Local development (optional)

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
