from django.shortcuts import render
from django.db import connection, IntegrityError, InternalError
from django.contrib import messages

from datetime import date
from uuid import UUID
import uuid
import json
import random

def show_main(request):
    return render(request, "main.html")

def show_dashboard(request):

    playlists = []
    songs = set()
    podcasts = []
    albums = []
    user = []
    label = []

    # Dashboard untuk LABEL
    if "Label" in request.session['roles']:
        label = json.loads(request.session['label'])[0]
        roles = request.session['roles']

        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT a.judul
                            FROM label l
                            JOIN album a ON l.id = a.id_label
                            WHERE l.email = %s;
                           """, [label['email']])
            albums = cursor.fetchall()
            temp = [album[0] for album in albums]
            albums = json.dumps(temp)
    
    # Dashbord untuk PENGGUNA
    else:
        user = json.loads(request.session['user'])[0]
        roles = request.session['roles']

        if 'Pengguna Biasa' in roles:
            # Take all playlist that user have
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT judul
                                FROM user_playlist
                                WHERE email_pembuat = %s;
                               """, [user['email']])
                playlists = json.dumps(cursor.fetchall())

        if 'Artist' or 'Songwriter' in roles:
            # Take all songs that artist have
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT k.judul
                                FROM artist a
                                JOIN song s ON a.id = s.id_artist
                                JOIN konten k ON s.id_konten = k.id
                                WHERE a.email_akun = %s;
                               """, [user['email']])
                temp = cursor.fetchall()
                for t in temp:
                    songs.add(t)

            # Take all songs that songwriter have
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT k.judul
                                FROM songwriter sw
                                JOIN songwriter_write_song sws ON sw.id = sws.id_songwriter
                                JOIN song s ON sws.id_song = s.id_konten
                                JOIN konten k ON s.id_konten = k.id
                                WHERE sw.email_akun = %s;
                               """, [user['email']])
                temp = cursor.fetchall()
                for t in temp:
                    songs.add(t)

                songs = json.dumps(list(songs))
        
        if 'Podcaster' in roles:
            # Take all podcasts that podcaster have
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT k.judul
                                FROM podcast p
                                JOIN konten k ON p.id_konten = k.id
                                WHERE p.email_podcaster = %s;
                               """, [user['email']])
                podcasts = json.dumps(cursor.fetchall())

    return render(request, "dashboard.html", {'user': user, 'label': label, 'roles': roles, 'albums': albums, 'playlists': playlists, 'songs': songs, 'podcasts': podcasts})    

def login(request):
    if (request.method == "POST"):
        email = request.POST['email']
        password = request.POST['password']

        with connection.cursor() as cursor:
            # [SQL] Otorisasi untuk mendapatkan data AKUN berdasarkan email dan password
            cursor.execute("""SELECT * FROM akun
                           WHERE email = %s AND password = %s
                           """, [email, password])
            user = cursor.fetchall()

            # [SQL] Otorisasi untuk mendapatkan data LABEL berdasarkan email dan password
            cursor.execute("""SELECT * FROM label
                            WHERE email = %s AND password = %s
                            """, [email, password])
            label = cursor.fetchall()

            # Error Handling jika email atau password tidak sesuai
            if user == [] and label == []:
                messages.error(request, "Email atau Password Anda salah")
                return render(request, "login.html")
            
            else:
                request.session['email'] = email

                if user != []:
                    # [SQL] Mendapatkan roles pengguna
                    cursor.execute("""
                        SELECT STRING_AGG(role, ', ') AS roles
                        FROM (
                            SELECT 'artist' AS role FROM artist WHERE email_akun = %s
                            UNION ALL
                            SELECT 'songwriter' AS role FROM songwriter WHERE email_akun = %s
                            UNION ALL
                            SELECT 'podcaster' AS role FROM podcaster WHERE email = %s
                        ) AS roles_table
                    """, [email, email, email])
                    roles = cursor.fetchone()
                    if roles[0] == None:
                        roles = ['Pengguna Biasa']
                    else:
                        roles = [role.capitalize() for role in roles[0].split(', ')]
                    request.session['roles'] = roles

                    # [SQL] Mendapatkan status langganan
                    cursor.execute("""
                                   SELECT 'premium' AS role
                                   FROM premium
                                   WHERE email = %s
                                   """, [email])
                    
                    if (cursor.fetchone() == None):
                        status_langganan = 'Non Premium'
                    else:
                        status_langganan = 'Premium'

                    # Simpan data pengguna ke session
                    user_columns = ['email', 'password', 'nama', 'gender', 'tempat_lahir', 'tanggal_lahir', 'is_verified', 'kota_asal']
                    user_data = []
                    for row in user:
                        row_dict = dict(zip(user_columns, row))

                        if isinstance(row_dict['tanggal_lahir'], date):
                            row_dict['tanggal_lahir'] = row_dict['tanggal_lahir'].isoformat()

                        user_data.append(row_dict)

                    user_data[0]['status_langganan'] = status_langganan

                    request.session['user'] = json.dumps(user_data)
                
                else:
                    request.session['roles'] = ['Label']

                    # Simpan data label ke session
                    label_column = ['id', 'nama', 'email', 'password', 'kontak', 'id_pemilik_hak_cipta']
                    label_data = []
                    for row in label:
                        row_dict = dict(zip(label_column, row))
                        for key, value in row_dict.items():
                            if isinstance(value, UUID):
                                row_dict[key] = str(value)
                        label_data.append(row_dict)
                    request.session['label'] = json.dumps(label_data)

                cursor.execute("""
                                CALL login_and_update_subscription(%s);
                               """, [email])

                return show_dashboard(request)
    
    return render(request, "login.html")

def register(request):
    if (request.method == "POST"):
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        gender = request.POST.get('gender')
        tempat_lahir = request.POST.get('tempat_lahir')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        kota_asal = request.POST.get('kota_asal')
        role = request.POST.getlist('role')
        kontak = request.POST.get('kontak')

        with connection.cursor() as cursor:
            try:
                id_pemilik_hak_cipta = uuid.uuid4()

                # Register untuk AKUN
                if (kontak == None):
                    cursor.execute("""
                                INSERT INTO akun (email, password, nama, gender, tempat_lahir, tanggal_lahir, kota_asal)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, [email, password, nama, gender, tempat_lahir, tanggal_lahir, kota_asal])

                    if 'artist' or 'songwriter' in role:
                        cursor.execute("""
                                        INSERT INTO pemilik_hak_cipta (id, rate_royalti)
                                        VALUES (%s, %s)
                                    """, [id_pemilik_hak_cipta, random.randint(1, 100)])

                    if 'artist' in role:
                        cursor.execute("""
                                        INSERT INTO artist (id, email_akun, id_pemilik_hak_cipta)
                                        VALUES (%s, %s, %s)
                                    """, [uuid.uuid4(), email, id_pemilik_hak_cipta])
                        
                    if 'songwriter' in role:
                        cursor.execute("""
                                    INSERT INTO songwriter (id, email_akun, id_pemilik_hak_cipta)
                                    VALUES (%s, %s, %s)
                                    """, [uuid.uuid4(), email, id_pemilik_hak_cipta])
                    
                    if 'podcaster' in role:
                        cursor.execute("""
                                        INSERT INTO podcaster (email)
                                        VALUES (%s)
                                    """, [email])
                        
                    if role != []:
                        # Change is_verified to True
                        cursor.execute("""
                                        UPDATE akun
                                        SET is_verified = TRUE
                                        WHERE email = %s
                                        """, [email])

                # Register untuk LABEL
                else:
                    cursor.execute("""
                                INSERT INTO pemilik_hak_cipta (id, rate_royalti)
                                VALUES (%s, %s)
                                """, [id_pemilik_hak_cipta, random.randint(1, 100)])

                    cursor.execute("""
                                INSERT INTO label (id, nama, email, password, kontak, id_pemilik_hak_cipta)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """, [uuid.uuid4(), nama, email, password, kontak, id_pemilik_hak_cipta])
            except InternalError as e:
                # Concate message error stop at "CONTEXT"
                error_message = str(e).split("CONTEXT")[0]
                return render(request, "register.html", {'error_message': error_message})
                
    return render(request, "register.html")

def logout(request):
    request.session.flush()
    request.session['roles'] = []
    return show_main(request)