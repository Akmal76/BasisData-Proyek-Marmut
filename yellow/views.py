from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import connection


# Dummy data for demonstration
PAKET_DATA = {
    '1_bulan': {'jenis': '1 Bulan', 'harga': 54900},
    '3_bulan': {'jenis': '3 Bulan', 'harga': 149700},
    '6_bulan': {'jenis': '6 Bulan', 'harga': 299400},
    '1_tahun': {'jenis': '1 Tahun', 'harga': 549900}
}

TRANSACTION_DATA = []

def get_paket_data():
    paket_data = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT jenis, harga FROM paket")
        rows = cursor.fetchall()
        for row in rows:
            key = row[0].replace(' ', '_').lower()
            paket_data[key] = {'jenis': row[0], 'harga': row[1]}
    return paket_data

def langganan_paket(request):
    user = request.session.get('user')
    # if not user:
    #     return redirect('main:login')

    paket_data = get_paket_data()
    
    if request.method == 'POST':
        jenis_paket_key = request.POST.get('jenis_paket')
        request.session['jenis_paket_key'] = jenis_paket_key
        return redirect('pembayaran')
    
    return render(request, 'langganan_paket.html', {'paket_data': paket_data, 'user': user})

def pembayaran(request):
    user = request.session.get('user')
    if not user:
        return redirect('main:login')

    jenis_paket_key = request.session.get('jenis_paket_key')
    if not jenis_paket_key:
        return redirect('langganan_paket')

    paket_data = get_paket_data()
    paket = paket_data[jenis_paket_key]

    if request.method == 'POST':
        metode_bayar = request.POST.get('metode_bayar')
        timestamp_dimulai = timezone.now()
        timestamp_berakhir = timestamp_dimulai + timezone.timedelta(days=30 * int(jenis_paket_key.split('_')[0]))
        transaction = {
            'id': len(TRANSACTION_DATA) + 1,
            'jenis_paket': paket['jenis'],
            'email': user['email'],
            'timestamp_dimulai': timestamp_dimulai,
            'timestamp_berakhir': timestamp_berakhir,
            'metode_bayar': metode_bayar,
            'nominal': paket['harga']
        }
        TRANSACTION_DATA.append(transaction)
        return redirect('riwayat_transaksi')
    
    return render(request, 'pembayaran.html', {'paket': paket, 'user': user})

def riwayat_transaksi(request):
    user = request.session.get('user')
    if not user:
        return redirect('main:login')

    user_transactions = [t for t in TRANSACTION_DATA if t['email'] == user['email']]
    user_transactions.sort(key=lambda x: x['timestamp_dimulai'], reverse=True)
    return render(request, 'riwayat_transaksi.html', {'transactions': user_transactions, 'user': user})

# FITUR SEARCH

SONGS = [
    {"title": "Love is in the air", "artist": "Artist1", "type": "SONG"},
    {"title": "What is love", "artist": "Artist2", "type": "SONG"},
    {"title": "Love is Blind Pod", "podcaster": "Podcaster1", "type": "PODCAST"},
    {"title": "90s Love Songs", "creator": "User1", "type": "USER PLAYLIST"},
]

# Dummy data for demonstration
# SONGS = [
#     {"type": "SONG", "title": "Love is in the air", "by": "Artist1"},
#     {"type": "SONG", "title": "What is love", "by": "Artist2"},
#     {"type": "PODCAST", "title": "Love is Blind Pod", "by": "Podcaster1"},
#     {"type": "USER PLAYLIST", "title": "90s Love Songs", "by": "User1"},
# ]

# def search(request):
#     query = request.GET.get('query', '').lower()
#     results = []

#     if query:
#         for song in SONGS:
#             if query in song["title"].lower():
#                 results.append(song)

#     return render(request, 'search.html', {'query': query, 'results': results})


def search(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        with connection.cursor() as cursor:
            sql_query = """
                SELECT SONG AS type, s.judul AS title, a.nama AS by 
                FROM song s
                JOIN artist a ON s.id_artist = a.id
                WHERE LOWER(s.judul) LIKE %s
                UNION
                SELECT 'PODCAST' AS type, p.judul AS title, pod.nama AS by 
                FROM podcast p
                JOIN podcaster pod ON p.email_podcaster = pod.email
                WHERE LOWER(p.judul) LIKE %s
                UNION
                SELECT USER_PLAYLIST AS type, up.judul AS title, up.email_pembuat AS by 
                FROM user_playlist up
                WHERE LOWER(up.judul) LIKE %s
            """
            cursor.execute(sql_query, ['%' + query.lower() + '%', '%' + query.lower() + '%', '%' + query.lower() + '%'])
            results = cursor.fetchall()

    return render(request, 'search.html', {'query': query, 'results': results})

#FITUR DOWNLOAD
def downloaded_songs(request):
    email = request.user.email  # Replace with actual user email
    songs = []

    with connection.cursor() as cursor:
        sql_query = """
            SELECT s.title, a.nama AS artist, d.timestamp_download
            FROM downloaded_songs ds
            JOIN songs s ON ds.id_song = s.id_konten
            JOIN artist a ON s.id_artist = a.id
            WHERE ds.email_downloader = %s
        """
        cursor.execute(sql_query, [email])
        songs = cursor.fetchall()

    return render(request, 'downloaded_songs.html', {'songs': songs})



