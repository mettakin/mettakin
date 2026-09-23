from django.db.models import Count

from .models import Experience, Phenomenon, Practice


def panels(request):
    """Practices and phenomena for the side panels, counting only what the visitor may see."""
    visible = Experience.objects.visible_to(request.user)

    def tags(model):
        return (
            model.objects.filter(experiences__in=visible)
            .annotate(count=Count("experiences", distinct=True))
            .order_by("-count", "name")[:20]
        )

    return {"panel_practices": tags(Practice), "panel_phenomena": tags(Phenomenon)}
