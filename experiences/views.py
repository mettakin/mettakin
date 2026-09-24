from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from ideas.models import Idea

from .forms import ExperienceForm
from .models import Experience, Phenomenon, Practice, Resonance

DRAFT = "draft"
DRAFT_FIELDS = ["title", "body", "visibility", "practice_name", "phenomena_names"]


def after(view_name, next_path):
    return redirect(f"{reverse(view_name)}?{urlencode({'next': next_path})}")


def browse(member):
    """What the side panels of a list page show: tags to browse and the ideas people want most."""
    visible = Experience.objects.visible_to(member)
    return {
        "practices": Practice.seen_in(visible)[:12],
        "phenomena": Phenomenon.seen_in(visible)[:12],
        "top_ideas": Idea.objects.ranked().filter(status=Idea.Status.OPEN)[:3],
    }


def home(request):
    top = request.GET.get("sort") == "top"
    order = ["-resonance_count", "-created_at"] if top else ["-created_at"]
    experiences = Experience.objects.listed(request.user).order_by(*order)[:50]
    return render(
        request,
        "experiences/list.html",
        {"experiences": experiences, "top": top} | browse(request.user),
    )


def experience(request, pk, slug):
    shown = get_object_or_404(Experience.objects.visible_to(request.user), pk=pk)
    if slug != shown.slug:
        return redirect(shown, permanent=True)
    resonated = (
        request.user.is_authenticated and shown.resonances.filter(member=request.user).exists()
    )
    context = {
        "experience": shown,
        "responses": Experience.objects.listed(request.user).filter(in_response_to=shown),
        "resonance_count": shown.resonances.count(),
        "resonated": resonated,
    }
    return render(request, "experiences/detail.html", context)


def write(request, respond_to=None):
    """Anyone can start writing. A signed-out writer's draft waits in the session as they join."""
    if request.user.is_authenticated and not request.user.has_consent:
        return after("consent", request.path)
    parent = None
    if respond_to:
        parent = get_object_or_404(Experience.objects.visible_to(request.user), pk=respond_to)
    draft = request.session.get(DRAFT) if request.method == "GET" else None
    form = ExperienceForm(request.POST or None, initial=draft)
    if form.is_valid():
        if not request.user.is_authenticated:
            request.session[DRAFT] = {field: request.POST.get(field, "") for field in DRAFT_FIELDS}
            return after("join", request.path)
        request.session.pop(DRAFT, None)
        return redirect(form.save(author=request.user, in_response_to=parent))
    return render(request, "experiences/write.html", {"form": form, "parent": parent})


@login_required
def edit(request, pk):
    mine = get_object_or_404(Experience, pk=pk, author=request.user)
    tags = {
        "practice_name": mine.practice.name if mine.practice else "",
        "phenomena_names": ", ".join(p.name for p in mine.phenomena.all()),
    }
    form = ExperienceForm(request.POST or None, instance=mine, initial=tags)
    if form.is_valid():
        return redirect(form.save(author=request.user, in_response_to=mine.in_response_to))
    return render(request, "experiences/write.html", {"form": form, "editing": mine})


@require_POST
def resonate(request, pk):
    shown = get_object_or_404(Experience.objects.visible_to(request.user), pk=pk)
    if not request.user.is_authenticated:
        return after("join", shown.get_absolute_url())
    resonance, created = Resonance.objects.get_or_create(member=request.user, experience=shown)
    if not created:
        resonance.delete()
    return redirect(shown)


def tag_page(request, tag, experiences):
    # A tag only exists for a visitor if they can see at least one experience with it.
    if not experiences:
        raise Http404
    context = {"tag": tag, "experiences": experiences} | browse(request.user)
    return render(request, "experiences/tag.html", context)


def practice(request, slug):
    tag = get_object_or_404(Practice, slug=slug)
    return tag_page(request, tag, Experience.objects.listed(request.user).filter(practice=tag))


def phenomenon(request, slug):
    tag = get_object_or_404(Phenomenon, slug=slug)
    return tag_page(request, tag, Experience.objects.listed(request.user).filter(phenomena=tag))
