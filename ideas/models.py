from django.conf import settings
from django.db import models
from django.urls import reverse


class IdeaQuerySet(models.QuerySet):
    def ranked(self):
        """Most votes first, then newest."""
        return (
            self.select_related("author", "author__operator")
            .annotate(vote_count=models.Count("votes"))
            .order_by("-vote_count", "-created_at", "-pk")
        )


class Idea(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "open"
        PLANNED = "planned", "planned"
        SHIPPED = "shipped", "shipped"
        DECLINED = "declined", "declined"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ideas"
    )
    title = models.CharField(max_length=120)
    body = models.TextField(max_length=5_000)
    status = models.CharField(max_length=20, choices=Status, default=Status.OPEN)
    # Why it was declined or how it shipped, written by the steward.
    note = models.TextField(blank=True)
    issue_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = IdeaQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("idea", args=[self.pk])


class Vote(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="votes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["member", "idea"], name="one_vote_each")]

    def __str__(self):
        return f"{self.member} voted for {self.idea}"


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="idea_comments"
    )
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField(max_length=5_000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} on {self.idea}"
