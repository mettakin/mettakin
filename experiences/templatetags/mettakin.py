from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def age(moment):
    """How long ago, as short as a news list shows it: 5m, 3h, 2d, 4mo."""
    seconds = (timezone.now() - moment).total_seconds()
    for unit, size in (("y", 31_536_000), ("mo", 2_592_000), ("d", 86_400), ("h", 3_600)):
        if seconds >= size:
            return f"{int(seconds // size)}{unit}"
    return f"{max(int(seconds // 60), 1)}m"
