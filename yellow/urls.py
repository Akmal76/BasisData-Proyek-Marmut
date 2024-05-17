from django.urls import path
from . import views

app_name = 'yellow';

urlpatterns = [
    path('langganan_paket/', views.langganan_paket, name='langganan_paket'),
    path('riwayat/', views.riwayat_transaksi, name='riwayat_transaksi'),
    path('pembayaran/', views.pembayaran, name='pembayaran'),
    path('search/', views.search, name='search'),
    path('results/', views.search, name='search'),
    path('downloaded/', views.downloaded_songs, name='downloaded_songs'),
]
