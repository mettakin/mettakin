from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from experiences import mcp

urlpatterns = [
    path("mcp", mcp.endpoint, name="mcp"),
    path("", include("experiences.urls")),
    path("", include("members.urls")),
    path("admin/", admin.site.urls),
    path("llms.txt", TemplateView.as_view(template_name="llms.txt", content_type="text/plain")),
]
