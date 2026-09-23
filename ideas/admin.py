from django.contrib import admin

from .models import Comment, Idea


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "created_at"]
    list_filter = ["status"]
    list_editable = ["status"]
    fields = ["title", "body", "author", "status", "note", "issue_url"]
    inlines = [CommentInline]
