from django.contrib import admin

from .models import Experience, Phenomenon, Practice


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "visibility", "created_at"]
    list_filter = ["visibility", "practice"]
    search_fields = ["title", "body"]


@admin.register(Practice, Phenomenon)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
