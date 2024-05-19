from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

import json
import uuid
from datetime import datetime

def create_album(request):
    if request.method == 'POST':

        # [SQL] Membuat album baru
        id_album = uuid.uuid4()
        jumlah_lagu = 1
        judul_album = request.POST.get('judul')
        total_durasi = request.POST.get('durasi')
        nama_label = request.POST.get('label')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT label.id
                            FROM label
                            WHERE label.nama = %s
                           """, [nama_label])
            id_label = cursor.fetchone()[0]

            cursor.execute("""
                            INSERT INTO album (id, judul, jumlah_lagu, id_label, total_durasi)
                            VALUES (%s, %s, %s, %s, %s)
                            """, [id_album, judul_album, jumlah_lagu, id_label, total_durasi])
        
        # [SQL] Membuat konten dan lagu baru
        id_konten = uuid.uuid4()
        judul_lagu = request.POST.get('judul_lagu')
        tanggal_liris = datetime.today().strftime('%Y-%m-%d')
        tahun = datetime.today().year
        artist = request.POST.get('artist')
        genres = request.POST.getlist('genre')
        songwriters = request.POST.getlist('songwriter')

        print(artist)
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT ar.id
                            FROM artist ar
                            JOIN akun a ON ar.email_akun = a.email
                            WHERE a.nama = %s;
                           """, [artist])
            artist = cursor.fetchone()[0]
            print(artist)

            cursor.execute("""
                            INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi)
                            VALUES (%s, %s, %s, %s, %s)
                           """, [id_konten, judul_lagu, tanggal_liris, tahun, total_durasi])
        
            cursor.execute("""
                           INSERT INTO song (id_konten, id_artist, id_album, total_play, total_download)
                            VALUES (%s, %s, %s, 0, 0)
                            """, [id_konten, artist, id_album])
            
            for genre in genres:
                cursor.execute("""
                                INSERT INTO genre (id_konten, genre)
                                VALUES (%s, %s)
                               """, [id_konten, genre])
            
            for songwriter in songwriters:
                cursor.execute("""
                                SELECT songwriter.id
                                FROM akun
                                JOIN songwriter ON akun.email = songwriter.email_akun
                                WHERE akun.nama = %s;
                               """, [songwriter])
                id_songwriter = cursor.fetchone()[0]

                cursor.execute("""
                                INSERT INTO songwriter_write_song (id_songwriter, id_song)
                                VALUES (%s, %s)
                               """, [id_songwriter, id_konten])
                
        return list_album(request)
    
    else:
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT *
                            FROM label
                           """)
            labels = cursor.fetchall()

            cursor.execute("""
                            SELECT 
                                artist.id AS Artist_ID,
                                akun.nama AS Nama,
                                akun.email AS Email
                            FROM artist
                            JOIN 
                                akun ON artist.email_akun = akun.email;
                           """)
            
            artists = cursor.fetchall()

            cursor.execute("""
                            SELECT 
                                songwriter.id AS Songwriter_ID,
                                akun.nama AS Nama,
                                akun.email AS Email
                            FROM 
                                songwriter
                            JOIN 
                                akun ON songwriter.email_akun = akun.email;
                            """)
            
            songwriters = cursor.fetchall()
        
            cursor.execute("""
                            SELECT DISTINCT genre
                            FROM genre
                           """)
            
            genres = cursor.fetchall()
        
        return render(request, 'create_album.html', {'labels': labels, 'user':json.loads(request.session['user'])[0], 'artists': artists, 'songwriters': songwriters, 'genres': genres})

def delete_album(request, id_album):
    with connection.cursor() as cursor:
            cursor.execute("""
                            DELETE FROM album
                            WHERE id = %s
                           """, [id_album])
            
    return list_album(request)

def create_lagu(request, id_album):
    if request.method == 'POST':
        
        # [SQL] Membuat konten dan lagu baru
        id_konten = uuid.uuid4()
        judul_lagu = request.POST.get('judul_lagu')
        tanggal_liris = datetime.today().strftime('%Y-%m-%d')
        tahun = datetime.today().year
        artist = request.POST.get('artist')
        genres = request.POST.getlist('genre')
        songwriters = request.POST.getlist('songwriter')
        total_durasi = request.POST.get('durasi')

        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT artist.id
                            FROM artist, akun
                            WHERE artist.email_akun = akun.email
                           """, [artist])
            artist = cursor.fetchone()[0]

            cursor.execute("""
                            INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi)
                            VALUES (%s, %s, %s, %s, %s)
                           """, [id_konten, judul_lagu, tanggal_liris, tahun, total_durasi])
        
            cursor.execute("""
                           INSERT INTO song (id_konten, id_artist, id_album, total_play, total_download)
                            VALUES (%s, %s, %s, 0, 0)
                            """, [id_konten, artist, id_album])
            
            for genre in genres:
                cursor.execute("""
                                INSERT INTO genre (id_konten, genre)
                                VALUES (%s, %s)
                               """, [id_konten, genre])
            
            for songwriter in songwriters:
                cursor.execute("""
                                SELECT songwriter.id
                                FROM akun
                                JOIN songwriter ON akun.email = songwriter.email_akun
                                WHERE akun.nama = %s;
                               """, [songwriter])
                id_songwriter = cursor.fetchone()[0]

                cursor.execute("""
                                INSERT INTO songwriter_write_song (id_songwriter, id_song)
                                VALUES (%s, %s)
                               """, [id_songwriter, id_konten])
                
        return list_album(request)
    
    else:
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT album.judul
                            FROM album
                            WHERE album.id = %s
                            """, [id_album])
            album = cursor.fetchone()[0]

            cursor.execute("""
                            SELECT *
                            FROM label
                           """)
            labels = cursor.fetchall()

            cursor.execute("""
                            SELECT *
                            FROM artist
                           """)
            
            artists = cursor.fetchall()

            cursor.execute("""
                            SELECT 
                                songwriter.id AS Songwriter_ID,
                                akun.nama AS Nama,
                                akun.email AS Email
                            FROM 
                                songwriter
                            JOIN 
                                akun ON songwriter.email_akun = akun.email;
                            """)
            
            songwriters = cursor.fetchall()
        
            cursor.execute("""
                            SELECT DISTINCT genre
                            FROM genre
                           """)
            
            genres = cursor.fetchall()
        
        return render(request, 'create_lagu.html', {'album': album, 'labels': labels, 'user':json.loads(request.session['user'])[0], 'artists': artists, 'songwriters': songwriters, 'genres': genres})

def delete_lagu(request, id_album, id_konten):
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM SONGWRITER_WRITE_SONG
            WHERE id_song = %s
        """, [id_konten])

        cursor.execute("""
            DELETE FROM AKUN_PLAY_SONG
            WHERE id_song = %s
        """, [id_konten])

        cursor.execute("""
            DELETE FROM PLAYLIST_SONG
            WHERE id_song = %s
        """, [id_konten])

        cursor.execute("""
            DELETE FROM ROYALTI
            WHERE id_song = %s
        """, [id_konten])

        cursor.execute("""
            DELETE FROM DOWNLOADED_SONG
            WHERE id_song = %s
        """, [id_konten])

        cursor.execute("""
            DELETE FROM SONG
            WHERE id_konten = %s
        """, [id_konten])
            
    return list_song(request, id_album)

def list_album(request):
    if 'Artist' in request.session['roles']:
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT 
                                album.id AS ID_Album,
                                album.judul AS Judul,
                                label.nama AS Label,
                                album.jumlah_lagu AS Jumlah_Lagu,
                                album.total_durasi AS Total_Durasi
                            FROM 
                                album
                            JOIN 
                                label ON album.id_label = label.id
                            JOIN 
                                song ON song.id_album = album.id
                            JOIN 
                                artist ON song.id_artist = artist.id
                            JOIN 
                                akun ON artist.email_akun = akun.email
                            WHERE 
                                akun.email = %s
                            GROUP BY 
                                album.id, album.judul, label.nama, album.jumlah_lagu, album.total_durasi;
                           """, [request.session['email']])
            albums = cursor.fetchall()
            albums = sorted(albums, key=lambda x: (x[2], x[1]))
    
    if 'Songwriter' in request.session['roles']:
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT DISTINCT
                                album.id AS ID_Album,
                                album.judul AS Judul,
                                label.nama AS Label,
                                album.jumlah_lagu AS Jumlah_Lagu,
                                album.total_durasi AS Total_Durasi
                            FROM 
                                album
                            JOIN 
                                label ON album.id_label = label.id
                            JOIN 
                                song ON song.id_album = album.id
                            JOIN 
                                songwriter_write_song ON songwriter_write_song.id_song = song.id_konten
                            JOIN 
                                songwriter ON songwriter.id = songwriter_write_song.id_songwriter
                            JOIN 
                                akun ON songwriter.email_akun = akun.email
                            WHERE 
                                akun.email = %s;
                           """, [request.session['email']])
            albums = cursor.fetchall()
            albums = sorted(albums, key=lambda x: (x[2], x[1]))
    
    if 'Label' in request.session['roles']:
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT
                                album.id AS ID_Album,
                                album.judul AS Judul,
                                album.jumlah_lagu AS Jumlah_Lagu,
                                album.total_durasi AS Total_Durasi
                            FROM 
                                album
                            JOIN 
                                label ON album.id_label = label.id
                            WHERE 
                                label.email = %s;
                           """, [request.session['email']])
            albums = cursor.fetchall()
            albums = sorted(albums, key=lambda x: (x[1]))

    return render(request, 'list_album.html', {'albums': albums, 'user_role': request.session['roles']})

def list_song(request, id_album):
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT
                            song.id_konten AS ID_Lagu,
                            konten.judul AS Judul,
                            konten.durasi AS Durasi,
                            song.total_play AS Total_Play,
                            song.total_download AS Total_Download
                        FROM 
                            song
                        JOIN 
                            konten ON song.id_konten = konten.id
                        WHERE 
                            song.id_album = %s;
                       """, [id_album])
        songs = cursor.fetchall()

        cursor.execute("""
                        SELECT album.judul
                        FROM album
                        WHERE album.id = %s
                       """, [id_album])
        album_title = cursor.fetchone()[0]

    return render(request, 'list_song.html', {'id_album': id_album, 'album_title': album_title, 'songs': songs})

def list_royalti(request):
    roles = request.session['roles']
    email = request.session['email']

    if 'Artist' in roles or 'Songwriter' in roles:
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT 
                                k.judul AS "Judul Lagu", 
                                a.judul AS "Judul Album", 
                                s.total_play AS "Total Play", 
                                s.total_download AS "Total Download", 
                                (s.total_play * phc.rate_royalti) AS "Total Royalti"
                            FROM 
                                song s
                            JOIN 
                                album a ON s.id_album = a.id
                            JOIN 
                                konten k ON s.id_konten = k.id
                            JOIN 
                                artist ar ON s.id_artist = ar.id
                            JOIN 
                                pemilik_hak_cipta phc ON ar.id_pemilik_hak_cipta = phc.id
                            WHERE 
                                ar.email_akun = %s;
                        """, [email])
            royalties = set(cursor.fetchall())

            cursor.execute("""
                           SELECT 
                                k.judul AS "Judul Lagu", 
                                a.judul AS "Judul Album", 
                                s.total_play AS "Total Play", 
                                s.total_download AS "Total Download", 
                                (s.total_play * phc.rate_royalti) AS "Total Royalti"
                            FROM 
                                songwriter sw
                            JOIN 
                                songwriter_write_song sws ON sw.id = sws.id_songwriter
                            JOIN 
                                song s ON sws.id_song = s.id_konten
                            JOIN 
                                album a ON s.id_album = a.id
                            JOIN 
                                konten k ON s.id_konten = k.id
                            JOIN 
                                pemilik_hak_cipta phc ON sw.id_pemilik_hak_cipta = phc.id
                            WHERE 
                                sw.email_akun = %s;
                        """, [email])
            
            royalties.update(cursor.fetchall())
            royalties = sorted(royalties, key=lambda x: (x[1], x[0]))


    elif 'Label' in roles:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT
                konten.judul AS judul_lagu,
                album.judul AS judul_album,
                song.total_play,
                song.total_download,
                (song.total_play * phc.rate_royalti) AS total_royalti
            FROM
                song
            JOIN
                album ON song.id_album = album.id
            JOIN
                konten ON song.id_konten = konten.id
            JOIN
                label ON album.id_label = label.id
            JOIN
                pemilik_hak_cipta phc ON label.id_pemilik_hak_cipta = phc.id
            WHERE
                label.email = %s
        """, [email])
        
            royalties = cursor.fetchall()
            royalties = sorted(royalties, key=lambda x: (x[1], x[0]))

    return render(request, 'list_royalti.html', {'royalties': royalties})
