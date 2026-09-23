from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from .forms import ExperienceForm
from .models import Experience, Phenomenon, Practice, Resonance


def home(request):
    experiences = Experience.objects.visible_to(request.user).annotate(
        resonance_count=Count("resonances")
    )
    return render(request, "experiences/list.html", {"experiences": experiences[:50]})


def experience(request, pk, slug):
    shown = get_object_or_404(Experience.objects.visible_to(request.user), pk=pk)
    if slug != shown.slug:
        return redirect(shown, permanent=True)
    resonated = (
        request.user.is_authenticated and shown.resonances.filter(member=request.user).exists()
    )
    context = {
        "experience": shown,
        "responses": Experience.objects.visible_to(request.user).filter(in_response_to=shown),
        "resonance_count": shown.resonances.count(),
        "resonated": resonated,
    }
    return render(request, "experiences/detail.html", context)


@login_required
def write(request, respond_to=None):
    if not request.user.has_consent:
        return redirect(f"{reverse('consent')}?{urlencode({'next': request.path})}")
    parent = None
    if respond_to:
        parent = get_object_or_404(Experience.objects.visible_to(request.user), pk=respond_to)
    form = ExperienceForm(request.POST or None)
    if form.is_valid():
        return redirect(form.save(author=request.user, in_response_to=parent))
    return render(request, "experiences/write.html", {"form": form, "parent": parent})


@login_required
@require_POST
def resonate(request, pk):
    shown = get_object_or_404(Experience.objects.visible_to(request.user), pk=pk)
    resonance, created = Resonance.objects.get_or_create(member=request.user, experience=shown)
    if not created:
        resonance.delete()
    return redirect(shown)


def tag_page(request, tag, experiences):
    # A tag only exists for a visitor if they can see at least one experience with it.
    if not experiences:
        raise Http404
    return render(request, "experiences/tag.html", {"tag": tag, "experiences": experiences})


def practice(request, slug):
    tag = get_object_or_404(Practice, slug=slug)
    return tag_page(request, tag, Experience.objects.visible_to(request.user).filter(practice=tag))


def phenomenon(request, slug):
    tag = get_object_or_404(Phenomenon, slug=slug)
    visible = Experience.objects.visible_to(request.user)
    return tag_page(request, tag, visible.filter(phenomena=tag))
