# views.py
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, HttpResponse
from .forms import VideoUploadForm, ImageUploadForm
from .utils import generate_video_frames, generate_webcam_frames, process_image
from django.conf import settings
import os
import time
import pandas as pd
import numpy as np
import cv2

def home(request):
    video_form = VideoUploadForm()
    image_form = ImageUploadForm()
    video_name = request.GET.get('video_name', None)
    image_name = request.GET.get('image_name', None)
    return render(request, 'home.html', {'video_form': video_form, 'image_form': image_form, 'video_name': video_name, 'image_name': image_name})

def video_feed(request):
    try:
        return StreamingHttpResponse(generate_webcam_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error: {e}")
        return render(request, 'error.html', {'error_message': str(e)})

def upload_and_process_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
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
    video_path = os.path.join('.', 'media', video_name)
    return StreamingHttpResponse(generate_video_frames(video_path), content_type='multipart/x-mixed-replace; boundary=frame')

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