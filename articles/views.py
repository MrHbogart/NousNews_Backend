from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article
from articles.serializers import ArticleIngestSerializer, ArticleSerializer
from core.viewsets import PublicReadModelViewSet


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class ArticleViewSet(PublicReadModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @action(detail=False, methods=["post"])
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


class ArticleSummaryView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        limit_raw = request.query_params.get("limit", "5")
        try:
            limit = int(limit_raw)
        except ValueError:
            limit = 5
        limit = max(1, min(limit, 10))

        articles = list(
            Article.objects.filter(is_public=True)
            .order_by("-published_at")
            .values("id", "source", "title", "published_at")[:limit]
        )
        summary_parts = []
        for entry in articles:
            title = (entry.get("title") or "").strip()
            source = (entry.get("source") or "").strip()
            if not title and not source:
                continue
            if title and source:
                summary_parts.append(f"{title} — {source}")
            else:
                summary_parts.append(title or source)

        summary = " · ".join(summary_parts) if summary_parts else "No crawled summaries yet."
        return Response(
            {
                "summary": summary,
                "count": len(articles),
                "items": articles,
                "as_of": timezone.now(),
            }
        )
