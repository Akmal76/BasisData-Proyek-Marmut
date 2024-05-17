from django.urls import path
from red.views import create_album, delete_album, create_lagu, delete_lagu, list_album, list_song, list_royalti

app_name = 'red'

urlpatterns = [
    path('create_album/', create_album, name='show_create_album'),
    path('delete_album/<str:id_album>', delete_album, name='delete_album'),
    path('create_lagu/<str:id_album>', create_lagu, name='show_create_lagu'),
    path('list_album/', list_album, name='list_album'),
    path('delete_lagu/<str:id_album>/<str:id_konten>', delete_lagu, name='delete_lagu'),
    path('list_song/<str:id_album>', list_song, name='list_song'),
    path('list_royalti/', list_royalti, name='list_royalti'),
]