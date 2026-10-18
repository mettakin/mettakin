from django.contrib import admin, messages

from . import github
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
    actions = ["send_to_builders"]

    # The click is the moderation step: nothing reaches GitHub unread.
    @admin.action(description="Send to builders", permissions=["change"])
    def send_to_builders(self, request, queryset):
        if not github.is_set_up():
            self.message_user(request, "GitHub isn't set up.", messages.ERROR)
            return
        sent = 0
        for idea in queryset.filter(issue_url="").ranked():
            try:
                github.send(idea, request.build_absolute_uri(idea.get_absolute_url()))
            except github.GitHubError as error:
                self.message_user(request, f"GitHub said: {error}", messages.ERROR)
                break
            sent += 1
        self.message_user(request, f"Sent {sent} of {queryset.count()} to builders.")
