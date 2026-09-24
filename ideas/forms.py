from django import forms

from mettakin.forms import PlainLabels

from .models import Comment, Idea


class IdeaForm(PlainLabels, forms.ModelForm):
    class Meta:
        model = Idea
        fields = ["title", "body"]
        labels = {
            "title": "Give it a title",
            "body": "Tell us more",
        }


class CommentForm(PlainLabels, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": "Your thoughts"}
        widgets = {"body": forms.Textarea(attrs={"rows": 4})}
