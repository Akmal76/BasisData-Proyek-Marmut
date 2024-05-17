# urls.py
from django.urls import path
from . import views

app_name = 'podcast'

urlpatterns = [
    path('', views.chartdetail, name='chart'),
    path('top_20/<str:type_of_top_20>', views.top_20, name='top_20'),
]