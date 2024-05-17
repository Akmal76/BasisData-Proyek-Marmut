from django.urls import path
from main import views as main_views 
from . import views

urlpatterns = [
    path('podcast/<uuid:podcast_id>/', views.podcast, name='podcast'),
    path('chart/', views.get_chart_details, name='get_chart_details'),
    path('create_podcast/', views.create_podcast, name='create_podcast'),
    path('delete_podcast/<uuid:podcast_id>/', views.delete_podcast, name='delete_podcast'),
    path('list_podcasts/', views.podcast, name='podcast'),
    path('create_episode/<uuid:podcast_id>/', views.create_episode, name='create_episode'),
    path('delete_episode/<uuid:episode_id>/', views.delete_episode, name='delete_episode'),
    path('list_episodes/<uuid:podcast_id>/', views.episode, name='episode'),
]
