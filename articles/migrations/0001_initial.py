# Generated manually for initial articles schema
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_public", models.BooleanField(default=True)),
                ("url", models.URLField(max_length=1000, unique=True)),
                ("source", models.CharField(max_length=255)),
                ("published_at", models.DateTimeField()),
                ("fetched_at", models.DateTimeField()),
                ("title", models.TextField(blank=True, default="")),
                ("body", models.TextField(blank=True, default="")),
                ("language", models.CharField(blank=True, default="", max_length=16)),
            ],
            options={
                "ordering": ["-published_at"],
                "indexes": [
                    models.Index(fields=["published_at"], name="articles_art_published_at_idx"),
                    models.Index(fields=["source"], name="articles_art_source_idx"),
                ],
            },
        ),
    ]
