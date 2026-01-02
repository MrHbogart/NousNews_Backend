from django.urls import path

from api import views

urlpatterns = [
    path("health/", views.HealthCheckView.as_view(), name="health"),
    path("crawl/trigger/", views.CrawlTriggerView.as_view(), name="crawl-trigger"),
    path("crawler/articles/", views.ArticleIngestView.as_view(), name="crawler-article-ingest"),
    path("articles/", views.ArticleListView.as_view(), name="article-list"),
]
