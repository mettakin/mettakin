from django.contrib.auth import views as auth
from django.urls import path

from . import views
from .forms import SignInForm

urlpatterns = [
    path("join/", views.join, name="join"),
    path(
        "login/",
        auth.LoginView.as_view(template_name="members/login.html", form_class=SignInForm),
        name="login",
    ),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("consent/", views.consent, name="consent"),
    path("me/", views.me, name="me"),
    path("me/export/", views.export, name="export"),
    path("me/withdraw-consent/", views.withdraw_consent, name="withdraw_consent"),
    path("me/delete/", views.delete, name="delete"),
]
