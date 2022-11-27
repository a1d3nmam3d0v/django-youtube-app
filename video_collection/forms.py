from django import forms
from .models import Video


class VideoForm(forms.ModelForm):
    # describes how forms are shown on the webpage
    class Meta:
        # fields from Video class/model that are shown in the form
        model = Video
        fields = {"name", "url", "notes"}


class SearchForm(forms.Form):  # forms.Form = basic django form
    search_term = forms.CharField()
