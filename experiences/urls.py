from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("write/", views.write, name="write"),
    path("e/<int:respond_to>/respond/", views.write, name="respond"),
    path("e/<int:pk>/resonate/", views.resonate, name="resonate"),
    # Last, so its slug doesn't swallow "respond" and "resonate".
    path("e/<int:pk>/<slug:slug>/", views.experience, name="experience"),
    path("practice/<slug:slug>/", views.practice, name="practice"),
    path("phenomenon/<slug:slug>/", views.phenomenon, name="phenomenon"),
]
