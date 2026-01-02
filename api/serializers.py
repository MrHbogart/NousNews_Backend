from rest_framework import serializers

from api.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "url",
            "source_domain",
            "published_at",
            "fetched_at",
            "headline",
            "body",
            "language",
            "rule_pass",
            "rule_reason",
            "ft_label",
            "ft_score",
            "tf_label",
            "tf_score",
        ]
