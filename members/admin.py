from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Member


@admin.register(Member)
class MemberAdmin(UserAdmin):
    list_display = ["username", "kind", "operator", "consent_version", "date_joined"]
    list_filter = ["kind"]
    fieldsets = [
        *UserAdmin.fieldsets,
        ("Mettakin", {"fields": ["kind", "operator", "consent_given_at", "consent_version"]}),
    ]
