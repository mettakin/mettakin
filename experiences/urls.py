from django.urls import path

from . import views

# Slugs are <str:...> because tags and titles can be in any language.
# Actions live outside /e/<pk>/ so no title's slug can collide with them.
urlpatterns = [
    path("", views.home, name="home"),
    path("write/", views.write, name="write"),
    path("respond/<int:respond_to>/", views.write, name="respond"),
    path("resonate/<int:pk>/", views.resonate, name="resonate"),
    path("edit/<int:pk>/", views.edit, name="edit"),
    path("e/<int:pk>/<str:slug>/", views.experience, name="experience"),
    path("practice/<str:slug>/", views.practice, name="practice"),
    path("phenomenon/<str:slug>/", views.phenomenon, name="phenomenon"),
]
