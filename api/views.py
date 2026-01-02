import json
import os
from datetime import datetime
from urllib import request as urllib_request
from urllib.error import URLError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Article, CrawlTask
from api.serializers import ArticleSerializer


def _is_crawler_authorized(request) -> bool:
    token = os.getenv("CRAWLER_API_TOKEN", "").strip()
    if not token:
        return True
    header_token = request.headers.get("X-API-Token")
    if header_token:
        return header_token == token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip() == token
    return False


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"})


class CrawlTriggerView(APIView):
    def post(self, request):
        source = request.data.get("source", "manual")
        action = request.data.get("action", "crawl")
        value = request.data.get("value")
        task = CrawlTask.objects.create(source=source, status="queued")
        crawler_url = os.getenv("CRAWLER_BASE_URL", "http://crawler:8081").rstrip("/")
        payload_data = {"task_id": task.id, "source": source, "action": action}
        if value is not None:
            payload_data["value"] = value
        payload = json.dumps(payload_data).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        token = os.getenv("CRAWLER_API_TOKEN", "").strip()
        if token:
            headers["X-API-Token"] = token
        req = urllib_request.Request(
            f"{crawler_url}/api/commands",
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            timeout = float(os.getenv("CRAWLER_TIMEOUT_SECONDS", "5"))
            with urllib_request.urlopen(req, timeout=timeout) as response:
                if response.status not in (200, 202):
                    task.status = "failed"
                    task.notes = f"Crawler response status {response.status}"
                    task.save(update_fields=["status", "notes"])
                    return Response(
                        {"status": "failed", "detail": "Crawler rejected request."},
                        status=status.HTTP_502_BAD_GATEWAY,
                    )
        except URLError as exc:
            task.status = "failed"
            task.notes = f"Crawler unreachable: {exc}"
            task.save(update_fields=["status", "notes"])
            return Response(
                {"status": "failed", "detail": "Crawler unreachable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        task.status = "running"
        task.notes = f"Command accepted: {action}"
        task.save(update_fields=["status", "notes"])

        return Response(
            {"status": "accepted", "task_id": task.id, "source": source, "action": action},
            status=status.HTTP_202_ACCEPTED,
        )


class ArticleIngestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if not _is_crawler_authorized(request):
            return Response({"detail": "Unauthorized."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = ArticleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        url = data.pop("url")
        article, created = Article.objects.update_or_create(url=url, defaults=data)
        return Response(
            {"status": "ok", "id": article.id, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ArticleListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        limit = request.query_params.get("limit", "50")
        try:
            limit_value = max(1, min(500, int(limit)))
        except (TypeError, ValueError):
            limit_value = 50
        queryset = Article.objects.order_by("-published_at")[:limit_value]
        serializer = ArticleSerializer(queryset, many=True)
        return Response(serializer.data)
