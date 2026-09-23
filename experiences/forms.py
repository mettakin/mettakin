from django import forms

from .models import Experience, Phenomenon, Practice


class ExperienceForm(forms.ModelForm):
    practice_name = forms.CharField(
        label="Practice", required=False, help_text="Vipassana, zazen, metta, just sitting..."
    )
    phenomena_names = forms.CharField(
        label="What was it like?",
        required=False,
        help_text="A few words, separated by commas: light, fear, body dissolving...",
    )

    class Meta:
        model = Experience
        fields = ["title", "body", "visibility"]
        labels = {"title": "In one line", "body": "What happened?"}
        widgets = {"visibility": forms.RadioSelect}

    def save(self, author, in_response_to=None):
        experience = super().save(commit=False)
        experience.author = author
        experience.in_response_to = in_response_to
        practices = Practice.from_names(self.cleaned_data["practice_name"])
        experience.practice = practices[0] if practices else None
        experience.save()
        experience.phenomena.set(Phenomenon.from_names(self.cleaned_data["phenomena_names"]))
        return experience
