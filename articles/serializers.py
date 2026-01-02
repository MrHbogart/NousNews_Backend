from rest_framework import serializers

from articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "url",
            "source",
            "published_at",
            "fetched_at",
            "title",
            "body",
            "language",
            "is_public",
        ]
        read_only_fields = ["id"]


class ArticleIngestSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=1000)
    source = serializers.CharField(max_length=255)
    published_at = serializers.DateTimeField()
    fetched_at = serializers.DateTimeField()
    title = serializers.CharField(allow_blank=True, required=False, default="")
    body = serializers.CharField(allow_blank=True, required=False, default="")
    language = serializers.CharField(allow_blank=True, required=False, default="")
