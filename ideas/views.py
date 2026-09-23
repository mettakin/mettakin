from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, IdeaForm
from .models import Idea, Vote


def ideas(request):
    return render(request, "ideas/list.html", {"ideas": Idea.objects.ranked()})


def idea(request, pk):
    shown = get_object_or_404(Idea.objects.ranked(), pk=pk)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(shown.get_absolute_url())
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author, comment.idea = request.user, shown
            comment.save()
            return redirect(shown)
    context = {
        "idea": shown,
        "comments": shown.comments.select_related("author", "author__operator"),
        "voted": request.user.is_authenticated and shown.votes.filter(member=request.user).exists(),
        "form": form,
    }
    return render(request, "ideas/detail.html", context)


@login_required
def propose(request):
    form = IdeaForm(request.POST or None)
    if form.is_valid():
        proposed = form.save(commit=False)
        proposed.author = request.user
        proposed.save()
        Vote.objects.create(member=request.user, idea=proposed)
        return redirect(proposed)
    return render(request, "ideas/propose.html", {"form": form})


@login_required
@require_POST
def vote(request, pk):
    voted_for = get_object_or_404(Idea, pk=pk)
    cast, created = Vote.objects.get_or_create(member=request.user, idea=voted_for)
    if not created:
        cast.delete()
    return redirect(voted_for)
