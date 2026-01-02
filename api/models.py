from django.db import models


class CrawlTask(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    source = models.CharField(max_length=120, default="manual")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="queued")
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.id}:{self.source}:{self.status}"


class Article(models.Model):
    url = models.URLField(max_length=1000, unique=True)
    source_domain = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    fetched_at = models.DateTimeField()
    headline = models.TextField(blank=True, default="")
    body = models.TextField(blank=True, default="")
    language = models.CharField(max_length=16, blank=True, default="")
    rule_pass = models.BooleanField(default=True)
    rule_reason = models.CharField(max_length=255, blank=True, default="")
    ft_label = models.CharField(max_length=64, blank=True, default="")
    ft_score = models.FloatField(blank=True, null=True)
    tf_label = models.CharField(max_length=64, blank=True, default="")
    tf_score = models.FloatField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["published_at"]),
            models.Index(fields=["source_domain"]),
            models.Index(fields=["fetched_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.source_domain}:{self.published_at:%Y-%m-%d}"
