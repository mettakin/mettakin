from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from members.models import CONSENT_VERSION


class Tag(models.Model):
    MAX_LENGTH = 60

    name = models.CharField(max_length=MAX_LENGTH)
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True, allow_unicode=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def named(cls, name):
        """The tag for this name, created if new. None when the name has no letters."""
        slug = slugify(name, allow_unicode=True)
        if not slug:
            return None
        return cls.objects.get_or_create(slug=slug, defaults={"name": name.strip()})[0]

    @classmethod
    def seen_in(cls, experiences):
        """Tags used by these experiences, most used first, each with its count."""
        return (
            cls.objects.filter(experiences__in=experiences)
            .annotate(count=models.Count("experiences", distinct=True))
            .order_by("-count", "name")
        )

    @classmethod
    def from_names(cls, names):
        tags = (cls.named(name) for name in names)
        return list({tag.pk: tag for tag in tags if tag}.values())


class Practice(Tag):
    def get_absolute_url(self):
        return reverse("practice", args=[self.slug])


class Phenomenon(Tag):
    class Meta(Tag.Meta):
        verbose_name_plural = "phenomena"

    def get_absolute_url(self):
        return reverse("phenomenon", args=[self.slug])


class ExperienceQuerySet(models.QuerySet):
    def visible_to(self, member):
        # Withdrawing consent hides everything the member wrote until they consent again.
        visible = self.filter(author__consent_version=CONSENT_VERSION)
        if not member.is_authenticated:
            visible = visible.filter(visibility=Experience.Visibility.PUBLIC)
        return visible.select_related("author", "author__operator", "practice")


class Experience(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public: open to the web and search"
        COMMUNITY = "community", "Community: only signed-in members"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experiences"
    )
    title = models.CharField(max_length=120)
    body = models.TextField(max_length=20_000)
    practice = models.ForeignKey(
        Practice, null=True, blank=True, on_delete=models.SET_NULL, related_name="experiences"
    )
    phenomena = models.ManyToManyField(Phenomenon, blank=True, related_name="experiences")
    visibility = models.CharField(max_length=20, choices=Visibility)
    in_response_to = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="responses"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ExperienceQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("experience", args=[self.pk, self.slug])

    @property
    def slug(self):
        return slugify(self.title, allow_unicode=True) or "-"


class Resonance(models.Model):
    """A member saying: this happened to me too."""

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resonances"
    )
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name="resonances")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["member", "experience"], name="one_resonance_each")
        ]

    def __str__(self):
        return f"{self.member} resonated with {self.experience}"
