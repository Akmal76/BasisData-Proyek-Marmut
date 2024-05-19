from django.urls import path
from main.views import show_main, show_dashboard, login, register, logout

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('dashboard/', show_dashboard, name='show_dashboard'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
]