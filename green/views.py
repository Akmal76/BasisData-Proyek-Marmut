from datetime import datetime
from time import timezone
import django
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from django.db import IntegrityError, InternalError, connection,transaction



def tambah_playlist(request):
    return render(request, 'tambah_playlist.html')


@csrf_exempt
def hapus_playlist(request,playlist_id):
    try:
        playlist_id = uuid.UUID(str(playlist_id))
    except ValueError:
        return HttpResponseBadRequest("Invalid playlist_id")
    
    if request.method == 'POST':
        try:
            playlist_id = uuid.UUID(str(playlist_id))
        except ValueError:
            return HttpResponseBadRequest("Invalid playlist_id")

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM USER_PLAYLIST WHERE id_playlist = %s", [playlist_id])

        return redirect("/green/kelola_playlist_terisi/")

    return HttpResponseNotFound("Invalid request method")

@csrf_exempt
def hapus_lagu(request):
    judul_lagu = request.POST.get('song.title')
    playlist_id = request.POST.get('playlist_id')
    print(judul_lagu)
    print(playlist_id)

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("select id from konten,playlist_song where konten.judul = %s",[judul_lagu])
            id_song = cursor.fetchone()
            cursor.execute("delete from playlist_song where id_song = %s",[id_song])
            
            redirect_string = "/green/detail_playlist/"+playlist_id

        return redirect(redirect_string)

def add_lagu_playlist(request,playlist_id):
    try:
        playlist_id = uuid.UUID(str(playlist_id))
    except ValueError:
        return HttpResponseBadRequest("Invalid playlist_id")

    with connection.cursor() as cursor:
        cursor.execute("SELECT konten.judul, akun.nama FROM song \
                        INNER JOIN konten ON song.id_konten = konten.id \
                        INNER JOIN artist ON song.id_artist = artist.id \
                        INNER JOIN akun ON artist.email_akun = akun.email")
        songs = cursor.fetchall()
    song_artist_list = ["{} - {}".format(song[0], song[1]) for song in songs]

    context = {
        'songs': song_artist_list,
        'playlist_id': playlist_id
    }

    return render(request, "add_lagu_playlist.html", context)

def add_playlist_lagu(request,song_id):
    email_user = request.session['email']
    try:
        song_id = uuid.UUID(str(song_id))
    except ValueError:
        return HttpResponseBadRequest("Invalid playlist_id")

    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_playlist, judul, jumlah_lagu, total_durasi FROM user_playlist WHERE email_pembuat = %s", [email_user])
        playlists = cursor.fetchall()
    
    context = {
        'playlists': playlists,
        'song_id': song_id
    }

    return render(request, "add_playlist_lagu.html", context)

@csrf_exempt
def tambah_lagu(request):
    if request.method == 'POST':
        
        playlist_id = request.POST.get('playlist_id')
        song_id = request.POST.get('song_id')
        judul_lagu = request.POST.get('judul_lagu')

        if judul_lagu:
            judul_lagu = judul_lagu.split(" - ")[0]
            
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_konten FROM song JOIN konten ON song.id_konten = konten.id WHERE konten.judul = %s", 
                    [judul_lagu]
                )
                song_idlist = cursor.fetchone()
                song_id = song_idlist[0]

        print(song_id)

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO playlist_song (id_playlist, id_song) VALUES (%s, %s)", [playlist_id, song_id])
        except InternalError as e:
            return JsonResponse({'error': str(e)}, status=500)
        
        redirect_url = f"/green/detail_playlist/{playlist_id}"

        return JsonResponse({'redirect_url': redirect_url})
    
    return HttpResponseNotFound("Method not allowed")

def ubah_playlist(request,playlist_id):
    try:
        playlist_id = uuid.UUID(str(playlist_id))
    except ValueError:
        return HttpResponseBadRequest("Invalid playlist_id")

    if not playlist_id:
        return HttpResponseNotFound("Playlist ID is required")

    with connection.cursor() as cursor:
        cursor.execute("SELECT judul, deskripsi FROM USER_PLAYLIST WHERE id_playlist = %s", [playlist_id])
        playlist_details = cursor.fetchone()

    if not playlist_details:
        return HttpResponseNotFound("Playlist not found")

    context = {
        'playlist_id': playlist_id,
        'judul': playlist_details[0],
        'deskripsi': playlist_details[1]
    }

    return render(request, 'ubah_playlist.html', context)

@csrf_exempt
def update_playlist(request):
    
    if request.method == 'POST':
        playlist_name = request.POST.get('playlistName')
        deskripsi = request.POST.get('deskripsi')

        if not playlist_name or not deskripsi:
            return HttpResponseBadRequest("Playlist name and description are required")

        email_pembuat = request.session.get('email')
        playlist_id = request.POST.get('playlist_id')

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM USER_PLAYLIST WHERE id_playlist = %s AND email_pembuat = %s", [playlist_id, email_pembuat])
            playlist_exists = cursor.fetchone()

            if not playlist_exists:
                return HttpResponseNotFound("Playlist not found or you don't have permission to edit it")

            cursor.execute("""
                UPDATE USER_PLAYLIST
                SET judul = %s, deskripsi = %s
                WHERE id_playlist = %s AND email_pembuat = %s
            """, [playlist_name, deskripsi, playlist_id, email_pembuat])

        return redirect("/green/kelola_playlist_terisi/")

    return HttpResponseNotFound("Invalid request method")

@csrf_exempt
def form_tambah_playlist(request):
    if request.method == 'POST':
        playlist_name = request.POST.get('playlistName')
        deskripsi = request.POST.get('deskripsi')

        if not playlist_name or not deskripsi:
            return HttpResponseBadRequest("Playlist name and description are required")

        random_uuid_user_playlist = uuid.uuid4()
        random_uuid_playlist = uuid.uuid4()
        today_date = datetime.today().date()
        email_pembuat = request.session['email']

        with connection.cursor() as cursor:
            cursor.execute(""" INSERT INTO PLAYLIST (id) VALUES (%s) """, [random_uuid_playlist])
            cursor.execute("""
                INSERT INTO USER_PLAYLIST (email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                email_pembuat, random_uuid_user_playlist, playlist_name, deskripsi, 0, today_date, random_uuid_playlist, 0
            ])

        return redirect("/green/kelola_playlist_terisi/")

    return HttpResponseNotFound()

def format_duration(duration):
        hours = duration // 60
        minutes = duration % 60
        return f"{hours} jam {minutes} menit"

def detail_playlist(request, playlist_id):
    try:
        playlist_id = uuid.UUID(str(playlist_id))
    except ValueError:
        return HttpResponseBadRequest("Invalid playlist_id")

    email_user = request.session.get('email')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_playlist WHERE id_playlist = %s AND email_pembuat = %s", [playlist_id, email_user])
        detail_playlist = cursor.fetchone()

        if not detail_playlist:
            return HttpResponseNotFound("Playlist not found")

        cursor.execute("""
            SELECT KONTEN.judul AS title, AKUN.nama AS artist, KONTEN.durasi AS duration, KONTEN.id AS id
            FROM playlist_song
            JOIN SONG ON playlist_song.id_song = SONG.id_konten
            JOIN KONTEN ON SONG.id_konten = KONTEN.id
            JOIN ARTIST ON SONG.id_artist = ARTIST.id
            JOIN AKUN ON ARTIST.email_akun = AKUN.email
            WHERE playlist_song.id_playlist = %s
        """, [playlist_id])
        songs_in_playlist = cursor.fetchall()

        formatted_songs_in_playlist = [
        {
            'title': row[0],
            'artist': row[1],
            'duration': format_duration(row[2]),
            'id': row[3]
        }
        for row in songs_in_playlist
    ]
        total_duration = detail_playlist[7]  
        formatted_total_duration = format_duration(total_duration)

    context = {
        'detail_playlist': detail_playlist,
        'total_durasi':formatted_total_duration,
        'songs_in_playlist': formatted_songs_in_playlist
    }
    return render(request, "detail_playlist.html", context)

def kelola_playlist_terisi(request):
    email_user = request.session['email']
    with connection.cursor() as cursor:
            cursor.execute("SELECT id_playlist, judul, jumlah_lagu, total_durasi FROM user_playlist WHERE email_pembuat = %s", [email_user])
            user_playlist = cursor.fetchall()

    print(user_playlist)

    context = {
        'playlist_query': user_playlist,
        'user': email_user
    }

    return render(request, "kelola_playlist_terisi.html", context)

def song_detail(request, song_id):
    try:
        song_uuid = uuid.UUID(str(song_id))
    except ValueError:
        song_uuid = None
    
    print(song_uuid)


    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM KONTEN WHERE id=%s",[song_uuid])
        # konten_detail = cursor.fetchall()
        # print(konten_detail)
        cursor.execute("""
            SELECT K.judul, 
                STRING_AGG(DISTINCT G.genre, ', ') AS genres,
                AK.nama AS artist, 
                STRING_AGG(DISTINCT SWR.nama, ', ') AS songwriters,
                K.durasi, 
                K.tanggal_rilis, 
                K.tahun, 
                SO.total_play, 
                SO.total_download,
                AL.judul AS album,
                K.id
            FROM KONTEN K
            JOIN SONG SO ON K.id = SO.id_konten
            JOIN ARTIST A ON SO.id_artist = A.id
            JOIN AKUN AK ON A.email_akun = AK.email
            LEFT JOIN ALBUM AL ON SO.id_album = AL.id
            JOIN SONGWRITER_WRITE_SONG SWS ON SO.id_konten = SWS.id_song
            JOIN SONGWRITER SW ON SWS.id_songwriter = SW.id
            JOIN AKUN SWR ON SW.email_akun = SWR.email
            LEFT JOIN GENRE G ON K.id = G.id_konten
            WHERE K.id = %s
            GROUP BY K.judul, 
                    AK.nama, 
                    K.durasi, 
                    K.tanggal_rilis, 
                    K.tahun, 
                    SO.total_play, 
                    SO.total_download,
                    AL.judul,
                    K.id
        """, [song_uuid])
        detail_song = cursor.fetchall()
        print(detail_song)

    context = {
        'detail_song': detail_song,
    }

    return render(request, 'song_detail.html', context)

@csrf_exempt
def update_play_count(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            song_id = data['song_id']
        except json.JSONDecodeError:
            song_id = request.POST.get('song_id')
        email_pemain = request.session['email']
        waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE SONG
                    SET total_play = total_play + 1
                    WHERE id_konten = %s
                """, [song_id])

                cursor.execute("""
                    INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu)
                    VALUES (%s, %s, %s)
                """, [email_pemain, song_id, waktu])

            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error'}, status=400)



@csrf_exempt
def download_lagu(request, song_id):
    if request.method == 'POST':
        email_downloader = request.session['email']
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT email FROM PREMIUM WHERE email = %s", [email_downloader])
                    premium_user = cursor.fetchone()

                    if not premium_user:
                        return JsonResponse({'error': 'User must have a premium account to download songs'}, status=403)

                    cursor.execute("INSERT INTO DOWNLOADED_SONG (id_song, email_downloader) VALUES (%s, %s)", [song_id, email_downloader])

                    cursor.execute("UPDATE SONG SET total_download = total_download + 0 WHERE id_konten = %s", [song_id])
                    
                    return JsonResponse({'success': 'Berhasil mengunduh lagu'}, status=201)
        
        except InternalError as e:
                return JsonResponse({'error': 'Lagu sudah pernah di unduh!'}, status=500)
        except IntegrityError as e:
                return JsonResponse({'error': 'Lagu sudah pernah di unduh!'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def shuffle_play(request):
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')
        email_user = request.session['email']

        try:
            with transaction.atomic():
                waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id_user_playlist FROM USER_PLAYLIST WHERE email_pembuat = %s AND id_playlist = %s", [email_user, playlist_id])
                    user_playlist_row = cursor.fetchone()
                    id_user_playlist = user_playlist_row[0]

                    cursor.execute("INSERT INTO AKUN_PLAY_USER_PLAYLIST (email_pemain, id_user_playlist, email_pembuat, waktu) VALUES (%s, %s, %s, %s)", [email_user, id_user_playlist, email_user, waktu])

                    cursor.execute("SELECT id_song FROM PLAYLIST_SONG WHERE id_playlist = %s", [playlist_id])
                    songs_in_playlist = cursor.fetchall()

                    for song_id in songs_in_playlist:
                        cursor.execute("INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu) VALUES (%s, %s, %s)", [email_user, song_id[0], waktu])

                        cursor.execute("UPDATE SONG SET total_play = total_play + 1 WHERE id_konten = %s", [song_id[0]])

            return JsonResponse({'success': 'Shuffle Play berhasil'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
