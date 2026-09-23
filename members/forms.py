from django.contrib.auth.forms import UserCreationForm

from .models import Member


class JoinForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ["username"]
        labels = {"username": "Name or pseudonym"}
