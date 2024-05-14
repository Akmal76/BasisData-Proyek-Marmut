from django.urls import path
from main.views import show_main, show_dashboard, login, show_register

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('dashboard/', show_dashboard, name='show_dashboard'),
    path('login/', login, name='login'),
    path('register/', show_register, name='show_register'),
]