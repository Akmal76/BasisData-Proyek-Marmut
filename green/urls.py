from django.urls import path
from green import views

app_name = 'green'

urlpatterns = [
    path('tambah_playlist/', views.tambah_playlist, name='tambah_playlist'),
    path('detail_playlist/<uuid:playlist_id>/', views.detail_playlist, name='detail_playlist'),
    path('add_playlist_lagu/<uuid:song_id>/', views.add_playlist_lagu, name='add_playlist_lagu'),
    path('tambah_lagu/', views.tambah_lagu, name='tambah_lagu'),
    path('kelola_playlist_terisi/', views.kelola_playlist_terisi, name='kelola_playlist_terisi'),
    path('song_detail/<uuid:song_id>/', views.song_detail, name='song_detail'),
    path('form_tambah_playlist/', views.form_tambah_playlist, name='form_tambah_playlist'),
    path('hapus_playlist/<uuid:playlist_id>/', views.hapus_playlist, name='hapus_playlist'),
    path('ubah_playlist/<uuid:playlist_id>/', views.ubah_playlist, name='ubah_playlist'),
    path('add_lagu_playlist/<uuid:playlist_id>/', views.add_lagu_playlist, name='add_lagu_playlist'),
    path('hapus_lagu/', views.hapus_lagu, name='hapus_lagu'),
    path('update_playlist/', views.update_playlist, name='update_playlist'),
    path('update_play_count/', views.update_play_count, name='update_play_count'),
    path('download_lagu/<uuid:song_id>/', views.download_lagu, name='download_lagu'),
    path('shuffle_play/', views.shuffle_play, name='shuffle_play'),
]
