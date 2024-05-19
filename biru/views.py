from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
import uuid
from django.utils import timezone

# Create your views here.
def get_podcast_details(request, podcast_id):
    with connection.cursor() as cursor:
        # Fetch podcast details
        cursor.execute("""
            SELECT K.judul, array_agg(G.genre), A.nama, K.durasi, K.tanggal_rilis, K.tahun
            FROM KONTEN K
            JOIN PODCAST P ON K.id = P.id_konten
            JOIN PODCASTER Po ON P.email_podcaster = Po.email
            JOIN AKUN A ON Po.email = A.email
            JOIN GENRE G ON K.id = G.id_konten
            WHERE K.id = %s
            GROUP BY K.judul, A.nama, K.durasi, K.tanggal_rilis, K.tahun
    """, [str(podcast_id)])

        podcast = cursor.fetchone()
        print(podcast)

        cursor.execute("""
            SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
            FROM EPISODE E
            WHERE E.id_konten_podcast = %s
            ORDER BY E.tanggal_rilis DESC
        """, [str(podcast_id)])

        episodes = cursor.fetchall()
        print(episodes)

    return render(request, 'podcastdetail.html', {'podcast': podcast, 'episodes': episodes})

from django.shortcuts import render
from django.db import connection

def get_chart_details(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types = cursor.fetchall()
        print("Chart Types:", chart_types)

        chart_details = {}
        for chart_type in chart_types:
            if chart_type[0] == 'Daily Top 20':
                cursor.execute("""
                    SELECT C.tipe, K.judul AS title, A.id AS artist, K.tanggal_rilis AS release_date, S.total_play AS plays
                    FROM CHART C
                    JOIN PLAYLIST_SONG PS ON C.id_playlist = PS.id_playlist
                    JOIN SONG S ON PS.id_song = S.id_konten
                    JOIN KONTEN K ON S.id_konten = K.id
                    JOIN ARTIST A ON S.id_artist = A.id
                    WHERE C.tipe = %s
                    ORDER BY S.total_play DESC
                    LIMIT 20
                """, [chart_type[0]])
                chart_details[chart_type[0]] = cursor.fetchall()

    print("Chart Details:", chart_details)

    return render(request, 'chartdetail.html', {'chart_details': chart_details, 'chart_types': chart_types})

def create_episode(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT K.judul
            FROM KONTEN K
            WHERE K.id = %s
        """, [podcast_id])
        podcast_title = cursor.fetchone()[0]  
        
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        duration = request.POST['duration']  
        id_episode = uuid.uuid4()
        current_time = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO EPISODE (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [id_episode, podcast_id, title, description, duration, current_time])

        return redirect('episodes', podcast_id=podcast_id)
        
    return render(request, 'createepisode.html', {'podcast_id': podcast_id, 'podcast_title': podcast_title})

def create_podcast(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        genre = request.POST.getlist('genre')
        duration = 0
        podcast_id = uuid.uuid4()
        current_time = timezone.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                VALUES (%s, %s, %s, %s, %s)
            """, [podcast_id, title, current_time, current_time.year, duration])

            for g in genre:
                cursor.execute("""
                    INSERT INTO GENRE (id_konten, genre)
                    VALUES (%s, %s)
                """, [podcast_id, g])

            cursor.execute("""
                INSERT INTO PODCAST (id_konten)
                VALUES (%s)
            """, [podcast_id])
        
        return redirect('podcast')  

    return render(request, 'createpodcast.html')

from django.db import IntegrityError

def delete_podcast(request, podcast_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM PODCAST
                    WHERE id_konten = %s
                """, [podcast_id])
                
                cursor.execute("""
                    DELETE FROM GENRE
                    WHERE id_konten = %s
                """, [podcast_id])
                
                cursor.execute("""
                    DELETE FROM KONTEN
                    WHERE id = %s
                """, [podcast_id])
        except IntegrityError as e:
            # Handle integrity error if needed
            print("IntegrityError:", e)
            pass

        return redirect('podcast')


def podcast(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT K.id, K.judul, COUNT(E.id_episode) AS jumlah_episode, COALESCE(SUM(E.durasi), 0) AS total_durasi
            FROM KONTEN K
            JOIN PODCAST P ON K.id = P.id_konten
            LEFT JOIN EPISODE E ON K.id = E.id_konten_podcast
            GROUP BY K.id, K.judul;
        """)
        podcasts = cursor.fetchall()
        print(podcasts)
    return render(request, 'podcast.html', {'podcasts': podcasts})

def delete_episode(request, episode_id, podcast_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM EPISODE
                WHERE id_episode = %s
            """, [episode_id])

        return redirect('episodes', podcast_id=podcast_id)

def list_episode(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT E.id_episode, E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
            FROM EPISODE E
            WHERE E.id_konten_podcast = %s
            ORDER BY E.tanggal_rilis DESC
        """, [podcast_id])
        episode = cursor.fetchall()
        print(episode)
    return render(request, 'episode.html', {'episode': episode, 'podcast_id': podcast_id})

def show_dashboard(request):
    # Your view logic here
    return render(request, 'dashboard.html')

def chart_view(request):
    return render(request, 'chart.html')

def get_chart_details_weekly(request):
    with connection.cursor() as cursor:
        # Fetch chart types
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types = cursor.fetchall()
        # print("Chart Types:", chart_types)

        # Fetch chart details for 'Daily Top 20' only
        chart_details = {}
        for chart_type in chart_types:
            if chart_type[0] == 'Weekly Top 20':
                cursor.execute("""
                    SELECT C.tipe, K.judul AS title, A.id AS artist, K.tanggal_rilis AS release_date, S.total_play AS plays
                    FROM CHART C
                    JOIN PLAYLIST_SONG PS ON C.id_playlist = PS.id_playlist
                    JOIN SONG S ON PS.id_song = S.id_konten
                    JOIN KONTEN K ON S.id_konten = K.id
                    JOIN ARTIST A ON S.id_artist = A.id
                    WHERE C.tipe = %s
                    ORDER BY S.total_play DESC
                    LIMIT 20
                """, [chart_type[0]])
                chart_details[chart_type[0]] = cursor.fetchall()

    # print("Chart Details:", chart_details)

    return render(request, 'chartdetailweekly.html', {'chart_details': chart_details, 'chart_types': chart_types})
