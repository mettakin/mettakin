from .models import Experience, Phenomenon, Practice


def panels(request):
    """Practices and phenomena for the side panels, counting only what the visitor may see."""
    visible = Experience.objects.visible_to(request.user)
    return {
        "panel_practices": Practice.seen_in(visible)[:20],
        "panel_phenomena": Phenomenon.seen_in(visible)[:20],
    }
