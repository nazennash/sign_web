# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload_video/', views.upload_and_process_video, name='upload_video'),
    path('process_video/<str:video_name>/', views.process_video, name='process_video'),
    path('process_youtube_video/<str:youtube_url>/', views.process_youtube_video, name='process_youtube_video'),
    path('upload_image/', views.upload_and_process_image, name='upload_image'),
    path('process_image/<str:image_name>/', views.process_image_view, name='process_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
