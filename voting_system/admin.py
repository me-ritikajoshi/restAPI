from django.contrib import admin
from .models import Post, Vote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "poster", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "url", "poster__username")
    list_select_related = ("poster",)
    ordering = ("-created_at",)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "voter")
    search_fields = ("post__title", "voter__username")
    autocomplete_fields = ("post", "voter")
