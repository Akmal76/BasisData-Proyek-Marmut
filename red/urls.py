from django.urls import path
from red.views import show_create_album, show_create_lagu, list_album, list_song, list_royalti

app_name = 'red'

urlpatterns = [
    path('create_album/', show_create_album, name='show_create_album'),
    path('create_lagu/', show_create_lagu, name='show_create_lagu'),
    path('list_album/', list_album, name='list_album'),
    path('list_song/', list_song, name='list_song'),
    path('list_royalti/', list_royalti, name='list_royalti'),
]