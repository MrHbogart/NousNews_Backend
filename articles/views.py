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

