import cv2
import base64
import json
import os
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from .utils import generate_webcam_frames, generate_video_frames, process_image, download_youtube_video
from threading import Thread

class VideoConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.streaming = False
        self.running = True
        self.thread = None
        print("WebSocket connection established")

    def disconnect(self, close_code):
        self.streaming = False
        self.running = False
        if self.thread is not None:
            self.thread.join()
        print("WebSocket connection closed")

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        video_type = data.get('video_type')
        video_path = data.get('video_path')

        if command == 'start':
            self.streaming = True
            if video_type == 'webcam':
                self.thread = Thread(target=self.stream_webcam)
                self.thread.start()
            elif video_type == 'video':
                video_full_path = os.path.join(settings.MEDIA_ROOT, video_path)
                self.thread = Thread(target=self.stream_video, args=(video_full_path,))
                self.thread.start()
            elif video_type == 'youtube':
                youtube_path = download_youtube_video(video_path)
                if youtube_path:
                    video_full_path = os.path.join(settings.MEDIA_ROOT, youtube_path)
                    self.thread = Thread(target=self.stream_video, args=(video_full_path,))
                    self.thread.start()
                else:
                    self.send(text_data=json.dumps({'error': 'Failed to download YouTube video'}))
            elif video_type == 'image':
                image_full_path = os.path.join(settings.MEDIA_ROOT, video_path)
                self.process_image(image_full_path)
        elif command == 'stop':
            self.streaming = False

    def stream_webcam(self):
        for frame in generate_webcam_frames():
            if not self.running or not self.streaming:
                break
            if frame is not None:
                encoded_frame = base64.b64encode(frame).decode('utf-8')
                self.send(text_data=json.dumps({'frame': encoded_frame}))
            else:
                print("No frame captured")

    def stream_video(self, video_path):
        for frame in generate_video_frames(video_path):
            if not self.running or not self.streaming:
                break
            if frame is not None:
                encoded_frame = base64.b64encode(frame).decode('utf-8')
                self.send(text_data=json.dumps({'frame': encoded_frame}))
            else:
                print("No frame captured")

    def process_image(self, image_path):
        frame = process_image(image_path)
        if not self.running or not self.streaming:
            return
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                encoded_frame = base64.b64encode(buffer).decode('utf-8')
                self.send(text_data=json.dumps({'frame': encoded_frame}))
            else:
                print("Failed to encode image frame")
        else:
            print("No frame processed")
