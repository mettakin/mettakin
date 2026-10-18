from django.urls import path

from . import views

urlpatterns = [
    path("ideas/", views.ideas, name="ideas"),
    path("ideas/new/", views.propose, name="propose"),
    path("ideas/github/", views.github_webhook, name="github_webhook"),
    path("ideas/<int:pk>/", views.idea, name="idea"),
    path("ideas/<int:pk>/vote/", views.vote, name="vote"),
]
