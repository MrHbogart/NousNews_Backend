from django.urls import include, path
from rest_framework.routers import DefaultRouter

from articles.views import ArticleViewSet, CrawlerCommandView, HealthView

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="articles")

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("crawler/command/", CrawlerCommandView.as_view(), name="crawler-command"),
    path("", include(router.urls)),
]
