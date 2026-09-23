from .models import Idea


def panel(request):
    """The open ideas with the most votes, for the side panel."""
    return {"panel_ideas": Idea.objects.ranked().filter(status=Idea.Status.OPEN)[:3]}
