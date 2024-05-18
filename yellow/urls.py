from django.urls import path
from . import views
from .views import *

app_name = 'yellow';

urlpatterns = [
    path('langganan_paket/', views.langganan_paket, name='langganan_paket'),
    path('riwayat_transaksi/', views.riwayat_transaksi, name='riwayat_transaksi'),
    path('pembayaran/<str:jenis>', views.pembayaran, name='pembayaran'),
    path('pembayaran_paket', views.pembayaran_paket, name='pembayaran_paket'),
    path('results/', views.search, name='search'),
    path('downloaded/', views.downloaded_songs, name='downloaded_songs'),
    path('delete_song/<uuid:id_song>/<str:email_downloader>', delete_song ,name= 'delete_song')
]
