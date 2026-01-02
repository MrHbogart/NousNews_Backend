from django.db import models

from core.models import PublishableModel


class Article(PublishableModel):
    url = models.URLField(max_length=1000, unique=True)
    source = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    fetched_at = models.DateTimeField()
    title = models.TextField(blank=True, default="")
    body = models.TextField(blank=True, default="")
    language = models.CharField(max_length=16, blank=True, default="")

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["published_at"]),
            models.Index(fields=["source"]),
        ]

    def __str__(self) -> str:
        return f"{self.source}:{self.published_at:%Y-%m-%d}"
