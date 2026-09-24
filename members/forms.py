from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from mettakin.forms import PlainLabels

from .models import Member

NAME = "Name or nickname"


class JoinForm(PlainLabels, UserCreationForm):
    class Meta:
        model = Member
        fields = ["username"]
        labels = {"username": NAME}
        help_texts = {"username": ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = "At least 8 characters."
        self.fields["password2"].label = "Password again"
        self.fields["password2"].help_text = ""


class SignInForm(PlainLabels, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = NAME
