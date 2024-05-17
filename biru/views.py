from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
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

        # Fetch podcast episodes
        cursor.execute("""
            SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
            FROM marmut.EPISODE E
            WHERE E.id_konten_podcast = %s
            ORDER BY E.tanggal_rilis DESC
        """, [str(podcast_id)])

        episodes = cursor.fetchall()
        print(episodes)

    return render(request, 'podcastdetail.html', {'podcast': podcast, 'episodes': episodes})

def get_chart_details(request):
    with connection.cursor() as cursor:
        # Fetch chart types
        cursor.execute("SELECT DISTINCT tipe FROM marmut.Chart")
        chart_types = cursor.fetchall()
        print("Chart Types:", chart_types) 

        # Fetch chart details
        chart_details = {}
        for chart_type in chart_types:
            cursor.execute("""
                SELECT C.tipe, K.judul AS title, A.id AS artist, K.tanggal_rilis AS release_date, S.total_play AS plays
                FROM marmut.CHART C
                JOIN marmut.PLAYLIST_SONG PS ON C.id_playlist = PS.id_playlist
                JOIN marmut.SONG S ON PS.id_song = S.id_konten
                JOIN marmut.KONTEN K ON S.id_konten = K.id
                JOIN marmut.ARTIST A ON S.id_artist = A.id
                WHERE C.tipe = %s
                ORDER BY S.total_play DESC
                LIMIT 20
            """, [chart_type[0]])
            chart_details[chart_type[0]] = cursor.fetchall()

    print("Chart Details:", chart_details) 

    return render(request, 'chartdetail.html', {'chart_details': chart_details, 'chart_types': chart_types})

def create_podcast(request):
    if request.method == 'POST':
        title = request.POST['title']
        genre = request.POST.getlist('genre')
        duration = request.POST['duration']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO marmut.KONTEN (judul, durasi)
                VALUES (%s, %s)
                RETURNING id
            """, [title, duration])
            podcast_id = cursor.fetchone()[0]

            for g in genre:
                cursor.execute("""
                    INSERT INTO marmut.GENRE (id_konten, genre)
                    VALUES (%s, %s)
                """, [podcast_id, g])

        return redirect('list_podcasts')

    return render(request, 'createpodcast.html')

def delete_podcast(request, podcast_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM marmut.KONTEN
                WHERE id = %s
            """, [podcast_id])

        return redirect('list_podcasts')

def podcast(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT K.id, K.judul, COUNT(E.id), SUM(E.durasi)
            FROM marmut.KONTEN K
            LEFT JOIN marmut.EPISODE E ON K.id = E.id_konten_podcast
            GROUP BY K.id
        """)
        podcasts = cursor.fetchall()

    return render(request, 'podcast.html', {'podcast': podcast})

def create_episode(request, podcast_id):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        duration = request.POST['duration']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO marmut.EPISODE (id_konten_podcast, judul, deskripsi, durasi)
                VALUES (%s, %s, %s, %s)
            """, [podcast_id, title, description, duration])

        return redirect('list_episodes', podcast_id=podcast_id)

    return render(request, 'createepisode.html')

def delete_episode(request, episode_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM marmut.EPISODE
                WHERE id = %s
            """, [episode_id])

        return redirect('list_episodes')

def episode(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
            FROM marmut.EPISODE E
            WHERE E.id_konten_podcast = %s
            ORDER BY E.tanggal_rilis DESC
        """, [podcast_id])
        episodes = cursor.fetchall()

    return render(request, 'episode.html', {'episode': episode})

def show_dashboard(request):
    # Your view logic here
    return render(request, 'dashboard.html')