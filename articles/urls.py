from django.urls import include, path
from rest_framework.routers import DefaultRouter

from articles.views import ArticleViewSet, HealthView

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="articles")

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("", include(router.urls)),
]
