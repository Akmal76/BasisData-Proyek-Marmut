from django.shortcuts import render
from django.db import connection
from django.contrib import messages

def show_main(request):
    return render(request, "main.html")

def show_dashboard(request):
    return render(request, "dashboard.html")

def login(request):
    if (request.method == "POST"):
        email = request.POST['email']
        password = request.POST['password']

        with connection.cursor() as cursor:
            # SQL untuk mendapatkan data AKUN berdasarkan email dan password
            cursor.execute("""SELECT * FROM akun
                           WHERE email = %s AND password = %s
                           """, [email, password])
            user = cursor.fetchall()

            # SQL untuk mendapatkan data LABEL berdasarkan email dan password
            cursor.execute("""SELECT * FROM label
                            WHERE email = %s AND password = %s
                            """, [email, password])
            label = cursor.fetchall()

            if user == [] and label == []:
                messages.error(request, "Email atau Password Anda salah")
                return render(request, "login.html")
            
            else:
                request.session['email'] = email

                if user != []:
                    # SQL untuk mendapatkan roles dari suatu AKUN
                    cursor.execute("""
                        SELECT STRING_AGG(role, ', ') AS roles
                        FROM (
                            SELECT 'nonpremium' AS role FROM nonpremium WHERE email = %s
                            UNION ALL
                            SELECT 'artist' AS role FROM artist WHERE email_akun = %s
                            UNION ALL
                            SELECT 'songwriter' AS role FROM songwriter WHERE email_akun = %s
                            UNION ALL
                            SELECT 'podcaster' AS role FROM podcaster WHERE email = %s
                            UNION ALL
                            SELECT 'premium' AS role FROM premium WHERE email = %s
                        ) AS roles_table
                    """, [email, email, email, email, email])
                    roles = cursor.fetchone()
                    request.session['roles'] = roles[0]
                
                else:
                    request.session['roles'] = "label"

                # print(user)
                # print(request.session['email'])
                # print(request.session['roles'])

                return render(request, "dashboard.html")
    
    return render(request, "login.html")

def show_register(request):
    return render(request, "register.html")