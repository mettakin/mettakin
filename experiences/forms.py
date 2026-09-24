from django import forms

from mettakin.forms import PlainLabels

from .models import Experience, Phenomenon, Practice, Tag

MAX_PHENOMENA = 10


class ExperienceForm(PlainLabels, forms.ModelForm):
    practice_name = forms.CharField(
        label="What were you practicing?",
        required=False,
        max_length=Tag.MAX_LENGTH,
        help_text="Vipassana, zazen, metta, yoga nidra, just sitting...",
    )
    phenomena_names = forms.CharField(
        label="What was it like?",
        required=False,
        help_text="A few words, separated by commas: light, fear, body dissolving...",
    )

    class Meta:
        model = Experience
        fields = ["title", "body", "visibility"]
        labels = {
            "title": "Give it a title",
            "body": "What happened?",
            "visibility": "Who can read it?",
        }
        widgets = {"visibility": forms.RadioSelect}

    def clean_phenomena_names(self):
        names = [n.strip() for n in self.cleaned_data["phenomena_names"].split(",") if n.strip()]
        if len(names) > MAX_PHENOMENA:
            raise forms.ValidationError(f"Up to {MAX_PHENOMENA}, please.")
        if any(len(n) > Tag.MAX_LENGTH for n in names):
            raise forms.ValidationError(f"Keep each one under {Tag.MAX_LENGTH} characters.")
        return names

    def save(self, author, in_response_to=None):
        experience = super().save(commit=False)
        experience.author = author
        experience.in_response_to = in_response_to
        experience.practice = Practice.named(self.cleaned_data["practice_name"])
        experience.save()
        experience.phenomena.set(Phenomenon.from_names(self.cleaned_data["phenomena_names"]))
        return experience
