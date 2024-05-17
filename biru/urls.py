from django.urls import path
from . import views

urlpatterns = [
    path('podcast/<uuid:podcast_id>/', views.get_podcast_details, name='get_podcast_details'),
    path('chart/', views.get_chart_details, name='get_chart_details')
]