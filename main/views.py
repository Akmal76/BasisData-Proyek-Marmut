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
            cursor.execute("SELECT * FROM akun \
                            WHERE email = %s AND password = %s", [email, password])
            user = cursor.fetchall()

            print(user)

            if user != []:
                return render(request, "dashboard.html")
            
    messages.error(request, "Email atau Password Anda salah")
    return render(request, "login.html")

def show_register(request):
    return render(request, "register.html")