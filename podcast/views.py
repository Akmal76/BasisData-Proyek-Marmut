# views.py
import datetime
from django.db import connection
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
            return redirect('episode', podcast_id=podcast_id)
    else:
        form = EpisodeForm(initial={'podcast': podcast_id})
    return render(request, 'createepisode.html', {'form': form})

def createpodcast(request):
    if request.method == 'POST':
        form = PodcastForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('podcast')
    else:
        form = PodcastForm()
    
    dummy_genres = ['Genre 1', 'Genre 2', 'Genre 3']  

    return render(request, 'createpodcast.html', {'form': form, 'dummy_genres': dummy_genres})


def delete_podcast(request, podcast_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM marmut.KONTEN
                WHERE id = %s
            """, [podcast_id])

        return redirect('podcast')
    
def delete_episode(request, episode_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM marmut.EPISODE
                WHERE id = %s
            """, [episode_id])

        return redirect('episode')
    
def get_podcast_details(request, podcast_id):
    with connection.cursor() as cursor:
        # Fetch podcast details
        cursor.execute("""
            SELECT K.judul, array_agg(G.genre), A.nama, K.durasi, K.tanggal_rilis, K.tahun
            FROM marmut.KONTEN K
            JOIN marmut.PODCAST P ON K.id = P.id_konten
            JOIN marmut.PODCASTER Po ON P.email_podcaster = Po.email
            JOIN marmut.AKUN A ON Po.email = A.email
            JOIN marmut.GENRE G ON K.id = G.id_konten
            WHERE K.id = %s
            GROUP BY K.judul, A.nama, K.durasi, K.tanggal_rilis, K.tahun
        """, [str(podcast_id)])

        podcast = cursor.fetchone()
        print(podcast)

        cursor.execute("""
            SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
            FROM marmut.EPISODE E
            WHERE E.id_konten_podcast = %s
            ORDER BY E.tanggal_rilis DESC
        """, [str(podcast_id)])

        episodes = cursor.fetchall()
        print(episodes)

    return render(request, 'podcastdetail.html', {'podcast': podcast, 'episode': episode})
