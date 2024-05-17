# views.py
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from .models import Podcast, Episode
from .forms import PodcastForm, EpisodeForm

def podcast(request):
    podcasts = Podcast.objects.all()
    dummy_data = [
        {'judul': 'Podcast1', 'jumlah_episode': 10, 'total_durasi': '100 menit'},
        {'judul': 'Podcast2', 'jumlah_episode': 3, 'total_durasi': '20 menit'},

        # Add more dummy data as needed
    ]
    return render(request, 'list_podcasts.html', {'podcasts': dummy_data})

def episode(request, podcast_id):
    podcast = Podcast.objects.get(pk=podcast_id)
    podcast = {'judul': 'Podcast1', 'jumlah_episode': 10, 'total_durasi': '100 menit'},
    episodes = Episode.objects.filter(podcast=podcast)
    episodes = [
        {'title': 'Episode 1', 'description' : "lorem ipsum dolor",'duration': '10 menit', "date": '2021-01-01'},
        {'title': 'Episode 2', 'description' : "sit amet",'duration': '7 menit', "date": '2021-01-02'},

    ]
    return render(request, 'view_episodes.html', {'podcast': podcast, 'episodes': episodes})

def createepisode(request, podcast_id):
    if request.method == 'POST':
        form = EpisodeForm(request.POST)
        if form.is_valid():
            form.save()
            podcast = Podcast.objects.get(pk=podcast_id)
            podcast.total_duration += form.cleaned_data['duration']
            podcast.save()
            return redirect('view_episodes', podcast_id=podcast_id)
    else:
        form = EpisodeForm(initial={'podcast': podcast_id})
    return render(request, 'add_episode.html', {'form': form})

def createpodcast(request):
    if request.method == 'POST':
        form = PodcastForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_podcasts')
    else:
        form = PodcastForm()
    
    dummy_genres = ['Genre 1', 'Genre 2', 'Genre 3']  

    return render(request, 'createpodcast.html', {'form': form, 'dummy_genres': dummy_genres})


def podcastdetail(request, podcast_id):
    podcast_data = {
        'judul': 'Podcast1',
        'durasi': '8 hours 20 minutes',
    }

    episode_data = [
        {'title': 'Episode 1', 'description': 'This is the first episode', 'duration': '59 minutes', 'date': '2024-03-18'},
        {'title': 'Episode 2', 'description': 'This is the second episode', 'duration': '1 hour 2 minutes', 'date': '2024-03-25'}
    ]

    return render(request, 'podcastdetail.html', {'episodes': episode_data})

