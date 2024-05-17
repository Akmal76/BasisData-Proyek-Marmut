# urls.py
from django.urls import path
from . import views

app_name = 'podcast'

urlpatterns = [
    path('', views.podcast, name='podcast'),
    path('<int:podcast_id>/', views.episode, name='episode'),
    path('add_episode/<int:podcast_id>', views.createepisode, name='createepisode'),
    path('create_podcast/', views.createpodcast, name='createpodcast'),
    path('play_podcast/<int:podcast_id>/', views.get_podcast_details, name='podcastdetaiil'),
]