from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
import uuid
from django.utils import timezone

# Create your views here.
def get_podcast_details(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                k.judul AS Judul, 
                string_agg(g.genre, ', ') AS "Genre(s)",
                a.nama AS Podcaster, 
                k.durasi AS "Total Durasi", 
                k.tanggal_rilis AS "Tanggal Rilis", 
                k.tahun AS Tahun
            FROM 
                konten k
            JOIN 
                podcast p ON k.id = p.id_konten
            JOIN 
                genre g ON k.id = g.id_konten
            JOIN 
                podcaster pc ON p.email_podcaster = pc.email
            JOIN 
                akun a ON pc.email = a.email
            WHERE 
                k.id = %s
            GROUP BY 
                k.judul, a.nama, k.durasi, k.tanggal_rilis, k.tahun;
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

    return render(request, 'podcastdetail.html', {'podcast': podcast, 'episodes': episodes})

from django.shortcuts import render
from django.db import connection

def get_chart_details(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types = cursor.fetchall()

        chart_details = {}
        for chart_type in chart_types:
            if chart_type[0] == 'Daily Top 20':
                cursor.execute("""
                    SELECT 
                        k.judul AS "Judul Lagu",
                        a.nama AS "Oleh (Nama Artis)",
                        k.tanggal_rilis AS "Tanggal Rilis",
                        s.total_play AS "Total Plays"
                    FROM 
                        song s
                    JOIN 
                        konten k ON s.id_konten = k.id
                    JOIN 
                        artist ar ON s.id_artist = ar.id
                    JOIN 
                        akun a ON ar.email_akun = a.email
                    WHERE 
                        s.total_play > 0
                    ORDER BY 
                        s.total_play DESC
                    LIMIT 20;
                """, [chart_type[0]])
                chart_details[chart_type[0]] = cursor.fetchall()

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

        return redirect('biru:episodes', podcast_id=podcast_id)
        
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
                INSERT INTO PODCAST (id_konten, email_podcaster)
                VALUES (%s, %s)
            """, [podcast_id, request.session['email']])
        
        print(request.session['email'])
        
        return redirect('biru:podcast')  

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

        return redirect('biru:podcast')


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
    return render(request, 'podcast.html', {'podcasts': podcasts})

def delete_episode(request, episode_id, podcast_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM EPISODE
                WHERE id_episode = %s
            """, [episode_id])

        return redirect('biru:episodes', podcast_id=podcast_id)

def list_episode(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT E.id_episode, E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
            FROM EPISODE E
            WHERE E.id_konten_podcast = %s
            ORDER BY E.tanggal_rilis DESC
        """, [podcast_id])
        episode = cursor.fetchall()
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

        # Fetch chart details for 'Daily Top 20' only
        chart_details = {}
        for chart_type in chart_types:
            if chart_type[0] == 'Weekly Top 20':
                cursor.execute("""
                    SELECT 
                        k.judul AS "Judul Lagu",
                        a.nama AS "Oleh (Nama Artis)",
                        k.tanggal_rilis AS "Tanggal Rilis",
                        s.total_play AS "Total Plays"
                    FROM 
                        song s
                    JOIN 
                        konten k ON s.id_konten = k.id
                    JOIN 
                        artist ar ON s.id_artist = ar.id
                    JOIN 
                        akun a ON ar.email_akun = a.email
                    WHERE 
                        s.total_play > 0
                    ORDER BY 
                        s.total_play DESC
                    LIMIT 20;
                """, [chart_type[0]])
                chart_details[chart_type[0]] = cursor.fetchall()

    return render(request, 'chartdetailweekly.html', {'chart_details': chart_details, 'chart_types': chart_types})

def get_chart_details_monthly(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types = cursor.fetchall()

        chart_details = {}
        for chart_type in chart_types:
            if chart_type[0] == 'Monthly Top 20':
                cursor.execute("""
                    SELECT 
                        k.judul AS "Judul Lagu",
                        a.nama AS "Oleh (Nama Artis)",
                        k.tanggal_rilis AS "Tanggal Rilis",
                        s.total_play AS "Total Plays"
                    FROM 
                        song s
                    JOIN 
                        konten k ON s.id_konten = k.id
                    JOIN 
                        artist ar ON s.id_artist = ar.id
                    JOIN 
                        akun a ON ar.email_akun = a.email
                    WHERE 
                        s.total_play > 0
                    ORDER BY 
                        s.total_play DESC
                    LIMIT 20;
                """, [chart_type[0]])
                chart_details[chart_type[0]] = cursor.fetchall()

    return render(request, 'chartdetailmonthly.html', {'chart_details': chart_details, 'chart_types': chart_types})

def get_chart_details_yearly(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT tipe FROM Chart")
        chart_types = cursor.fetchall()

        chart_details = {}
        for chart_type in chart_types:
            if chart_type[0] == 'Yearly Top 20':
                cursor.execute("""
                    SELECT 
                        k.judul AS "Judul Lagu",
                        a.nama AS "Oleh (Nama Artis)",
                        k.tanggal_rilis AS "Tanggal Rilis",
                        s.total_play AS "Total Plays"
                    FROM 
                        song s
                    JOIN 
                        konten k ON s.id_konten = k.id
                    JOIN 
                        artist ar ON s.id_artist = ar.id
                    JOIN 
                        akun a ON ar.email_akun = a.email
                    WHERE 
                        s.total_play > 0
                    ORDER BY 
                        s.total_play DESC
                    LIMIT 20;
                """, [chart_type[0]])
                chart_details[chart_type[0]] = cursor.fetchall()

    return render(request, 'chartdetailyearly.html', {'chart_details': chart_details, 'chart_types': chart_types})
