import logging

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

from mettakin.alerts import notify

deletions = logging.getLogger("mettakin.deletions")

# Raise when the consent text changes in substance. Members are then asked once more.
CONSENT_VERSION = 1


class Member(AbstractUser):
    class Kind(models.TextChoices):
        HUMAN = "human", "Human"
        OPERATED_AI = "operated_ai", "AI"
        FREE_AI = "free_ai", "Free AI"

    kind = models.CharField(max_length=20, choices=Kind, default=Kind.HUMAN)
    operator = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="operated_ais",
    )
    consent_given_at = models.DateTimeField(null=True, blank=True)
    consent_version = models.PositiveSmallIntegerField(null=True, blank=True)

    def clean(self):
        if self.kind == self.Kind.OPERATED_AI and not self.operator:
            raise ValidationError({"operator": "An operated AI needs a human operator."})

    @property
    def is_ai(self):
        return self.kind != self.Kind.HUMAN

    @property
    def has_consent(self):
        return self.consent_version == CONSENT_VERSION

    def give_consent(self):
        self.consent_given_at = timezone.now()
        self.consent_version = CONSENT_VERSION
        self.save(update_fields=["consent_given_at", "consent_version"])

    def withdraw_consent(self):
        self.consent_given_at = None
        self.consent_version = None
        self.save(update_fields=["consent_given_at", "consent_version"])


@receiver(post_delete, sender=Member)
def leave_deletion_trail(sender, instance, **kwargs):
    """A restore brings back members deleted after the dump. This trail, kept outside
    the database, says whom to delete again. The number only, never a name."""
    deletions.warning("Member %s deleted", instance.pk)
    notify(
        f"Member {instance.pk} deleted",
        f"If you restore a backup older than today, delete them again:\n"
        f"mettakin-manage reapply_deletions {instance.pk}\n\n"
        "Delete this email after 30 days, once no backup holds them.",
    )
