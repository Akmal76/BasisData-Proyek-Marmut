from django.shortcuts import render

def show_main(request):
    return render(request, "main.html")

def show_dashboard(request):
    return render(request, "dashboard.html")

def show_login(request):
    return render(request, "login.html")

def show_register(request):
    return render(request, "register.html")