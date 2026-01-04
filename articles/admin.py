from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("source", "published_at", "title", "is_public")
    list_filter = ("source", "is_public")
    search_fields = ("title", "body", "url")
    ordering = ("-published_at",)
