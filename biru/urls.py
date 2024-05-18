from django.urls import path
from main import views as main_views 
from biru.views import podcast, get_chart_details, chart_view, create_podcast, delete_podcast, create_episode, delete_episode, episode, get_podcast_details

urlpatterns = [
    path('podcast/<uuid:podcast_id>/', podcast, name='podcast'),
    path('podcasts/<int:podcast_id>/', get_podcast_details, name='get_podcast_details'),
    path('chartDetails/', get_chart_details, name='get_chart_details'),
    path('chart/', chart_view, name='chart'),
    path('create_podcast/', create_podcast, name='create_podcast'),
    path('delete_podcast/<uuid:podcast_id>/', delete_podcast, name='delete_podcast'),
    path('list_podcasts/', podcast, name='podcast'),
    path('create_episode/<uuid:podcast_id>/', create_episode, name='create_episode'),
    path('delete_episode/<uuid:episode_id>/', delete_episode, name='delete_episode'),
    path('list_episodes/<uuid:podcast_id>/', episode, name='episode'),
]
