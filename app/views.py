# views.py
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from .forms import VideoUploadForm
from .utils import generate_video_frames, generate_webcam_frames
from django.conf import settings
import os

def home(request):
    return render(request, 'home.html')

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
            return redirect('process_video', video_name=video_file.name)
    else:
        form = VideoUploadForm()
    
    return render(request, 'upload_video.html', {'form': form})

def process_video(request, video_name):
    video_path = os.path.join(settings.MEDIA_ROOT, video_name)
    return StreamingHttpResponse(generate_video_frames(video_path), content_type='multipart/x-mixed-replace; boundary=frame')
