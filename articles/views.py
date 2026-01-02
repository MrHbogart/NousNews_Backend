import json
import os
from urllib import request as urllib_request
from urllib.error import URLError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article
from articles.serializers import ArticleIngestSerializer, ArticleSerializer
from core.permissions import HasCrawlerToken, IsStaffOrReadOnly
from core.viewsets import PublicReadModelViewSet


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class ArticleViewSet(PublicReadModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsStaffOrReadOnly]

    @action(detail=False, methods=["post"], permission_classes=[HasCrawlerToken])
    def ingest(self, request):
        serializer = ArticleIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        url = data.pop("url")
        article, created = Article.objects.update_or_create(url=url, defaults=data)
        return Response(
            {"status": "ok", "id": article.id, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CrawlerCommandView(APIView):
    permission_classes = [HasCrawlerToken]

    def post(self, request):
        action = request.data.get("action", "crawl")
        value = request.data.get("value")
        crawler_url = os.getenv("CRAWLER_BASE_URL", "http://crawler:8081").rstrip("/")
        payload_data = {"action": action}
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
                    return Response(
                        {"status": "failed", "detail": "Crawler rejected request."},
                        status=status.HTTP_502_BAD_GATEWAY,
                    )
        except URLError as exc:
            return Response(
                {"status": "failed", "detail": f"Crawler unreachable: {exc}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"status": "accepted", "action": action}, status=status.HTTP_202_ACCEPTED)
