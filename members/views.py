from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import JoinForm


def safe_next(request, fallback="home"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
        return next_url
    return fallback


def join(request):
    form = JoinForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect(safe_next(request))
    return render(request, "members/join.html", {"form": form})


@login_required
def consent(request):
    if request.method == "POST":
        request.user.give_consent()
        return redirect(safe_next(request))
    return render(request, "members/consent.html", {"next": safe_next(request, "")})


@login_required
def me(request):
    return render(request, "members/me.html")


@login_required
def export(request):
    member = request.user
    data = {
        "name": member.username,
        "joined": member.date_joined,
        "consent_given_at": member.consent_given_at,
        "experiences": [
            {
                "title": e.title,
                "body": e.body,
                "practice": str(e.practice or ""),
                "phenomena": [str(p) for p in e.phenomena.all()],
                "visibility": e.visibility,
                "created_at": e.created_at,
            }
            for e in member.experiences.prefetch_related("phenomena").select_related("practice")
        ],
    }
    response = JsonResponse(data, json_dumps_params={"indent": 2})
    response["Content-Disposition"] = 'attachment; filename="mettakin.json"'
    return response


@login_required
@require_POST
def withdraw_consent(request):
    request.user.withdraw_consent()
    return redirect("me")


@login_required
@require_POST
def delete(request):
    member = request.user
    logout(request)
    member.delete()
    return redirect("home")
