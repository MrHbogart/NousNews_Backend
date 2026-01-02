# Generated manually for article schema
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.URLField(max_length=1000, unique=True)),
                ("source_domain", models.CharField(max_length=255)),
                ("published_at", models.DateTimeField()),
                ("fetched_at", models.DateTimeField()),
                ("headline", models.TextField(blank=True, default="")),
                ("body", models.TextField(blank=True, default="")),
                ("language", models.CharField(blank=True, default="", max_length=16)),
                ("rule_pass", models.BooleanField(default=True)),
                ("rule_reason", models.CharField(blank=True, default="", max_length=255)),
                ("ft_label", models.CharField(blank=True, default="", max_length=64)),
                ("ft_score", models.FloatField(blank=True, null=True)),
                ("tf_label", models.CharField(blank=True, default="", max_length=64)),
                ("tf_score", models.FloatField(blank=True, null=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["published_at"], name="api_article_published_at_idx"),
                    models.Index(fields=["source_domain"], name="api_article_source_domain_idx"),
                    models.Index(fields=["fetched_at"], name="api_article_fetched_at_idx"),
                ],
            },
        ),
    ]
