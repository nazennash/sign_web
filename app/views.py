# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from .forms import VideoUploadForm, ImageUploadForm
from .utils import generate_video_frames, process_image, download_youtube_video
from django.conf import settings
import os
import cv2

def home(request):
    video_form = VideoUploadForm()
    image_form = ImageUploadForm()
    video_name = request.GET.get('video_name', None)
    image_name = request.GET.get('image_name', None)
    youtube_url = request.GET.get('youtube_url', None)
    return render(request, 'home.html', {
        'video_form': video_form,
        'image_form': image_form,
        'video_name': video_name,
        'image_name': image_name,
        'youtube_url': youtube_url,
    })

def upload_and_process_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            youtube_url = form.cleaned_data.get('youtube_url')
            if youtube_url:
                filename = download_youtube_video(youtube_url)
                if filename:
                    return redirect(f'/?youtube_url={filename}')
            else:
                video_file = request.FILES['video']
                video_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
                with open(video_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                return redirect(f'/?video_name={video_file.name}')
    else:
        form = VideoUploadForm()
    
    return render(request, 'home.html', {'video_form': form})

def process_video(request, video_name):
    video_path = os.path.join(settings.MEDIA_ROOT, video_name)
    return StreamingHttpResponse(generate_video_frames(video_path), content_type='multipart/x-mixed-replace; boundary=frame')

def process_youtube_video(request, youtube_url):
    video_path = os.path.join(settings.MEDIA_ROOT, youtube_url)
    if os.path.exists(video_path):
        return StreamingHttpResponse(generate_video_frames(video_path), content_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return render(request, 'error.html', {'error_message': 'Video not found'})

def upload_and_process_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            image_path = os.path.join(settings.MEDIA_ROOT, image_file.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            return redirect(f'/?image_name={image_file.name}')
    else:
        form = ImageUploadForm()
    
    return render(request, 'home.html', {'image_form': form})

def process_image_view(request, image_name):
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)
    frame = process_image(image_path)
    ret, buffer = cv2.imencode('.jpg', frame)
    response = HttpResponse(buffer.tobytes(), content_type='image/jpeg')
    return response
