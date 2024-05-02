from django.urls import path
from main.views import show_main, show_dashboard, show_login, show_register

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('dashboard/', show_dashboard, name='show_dashboard'),
    path('login/', show_login, name='show_login'),
    path('register/', show_register, name='show_register'),
]