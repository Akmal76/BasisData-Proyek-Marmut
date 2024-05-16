from django.shortcuts import render
from django.db import connection
from django.contrib import messages

from datetime import date
from uuid import UUID

import json

def show_main(request):
    return render(request, "main.html")

def show_dashboard(request):

    # Dashbord untuk PENGGUNA

    if 'user' in request.session:
        user = json.loads(request.session['user'])[0]
        roles = request.session['roles']
        print(roles)
        return render(request, "dashboard.html", {'user': user, 'roles': roles})
    
    # Dashboard untuk LABEL

    elif 'label' in request.session:
        label = json.loads(request.session['label'])
        roles = request.session['roles']
        return render(request, "dashboard.html", {'label': label, 'roles': roles})

    return render(request, "dashboard.html")

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
                    request.session['roles'] = 'label'

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

                return show_dashboard(request)
    
    return render(request, "login.html")

def show_register(request):
    return render(request, "register.html")