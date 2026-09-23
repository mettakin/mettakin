from django import forms

from .models import Comment, Idea


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ["title", "body"]
        labels = {
            "title": "The idea in one line",
            "body": "Why it matters, and what it could look like",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": "Your thoughts"}
        widgets = {"body": forms.Textarea(attrs={"rows": 4})}
