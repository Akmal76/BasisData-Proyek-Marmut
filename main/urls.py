from django.urls import path
from main.views import show_dashboard

app_name = 'main'

urlpatterns = [
    path('', show_dashboard, name='show_dashboard'),
]