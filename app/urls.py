# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('upload/', views.upload_and_process_video, name='upload_video'),
    path('process_video/<str:video_name>/', views.process_video, name='process_video'),
]
