from django.urls import include, path
from rest_framework.routers import DefaultRouter

from articles.views import ArticleSummaryView, ArticleViewSet, HealthView

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="articles")

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("articles/summary/", ArticleSummaryView.as_view(), name="articles-summary"),
    path("", include(router.urls)),
]
