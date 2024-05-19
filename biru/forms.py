from django import forms

# Assuming you have a Genre model
# Replace Genre with your actual model name
from .models import Genre, Episode

class PodcastForm(forms.Form):
    judul = forms.CharField(label='Judul', max_length=100)
    genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(), label='Genre')
    durasi = forms.CharField(label='Durasi', max_length=50)

class EpisodeForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ['podcast', 'title', 'duration']