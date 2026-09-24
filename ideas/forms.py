from django import forms

from .models import Comment, Idea


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ["title", "body"]
        labels = {
            "title": "Give it a title",
            "body": "Tell us more",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": "Your thoughts"}
        widgets = {"body": forms.Textarea(attrs={"rows": 4})}
