# consumers.py
import cv2
import base64
from channels.generic.websocket import WebsocketConsumer
import json
import os
from django.conf import settings
from .utils import generate_webcam_frames, generate_video_frames, process_image

class VideoConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket connection established")

    def disconnect(self, close_code):
        print("WebSocket connection closed")

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        video_type = data.get('video_type')
        video_path = data.get('video_path')
        
        if command == 'start':
            if video_type == 'webcam':
                self.stream_webcam()
            elif video_type == 'video':
                self.stream_video(video_path)
            elif video_type == 'youtube':
                self.stream_video(video_path)
            elif video_type == 'image':
                self.process_image(video_path)
    
    def stream_webcam(self):
        for frame in generate_webcam_frames():
            if frame is not None:
                encoded_frame = base64.b64encode(frame).decode('utf-8')
                self.send(text_data=json.dumps({'frame': encoded_frame}))
            else:
                print("No frame captured")

    def stream_video(self, video_path):
        for frame in generate_video_frames(video_path):
            if frame is not None:
                encoded_frame = base64.b64encode(frame).decode('utf-8')
                self.send(text_data=json.dumps({'frame': encoded_frame}))
            else:
                print("No frame captured")

    def process_image(self, image_path):
        frame = process_image(image_path)
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                encoded_frame = base64.b64encode(buffer).decode('utf-8')
                self.send(text_data=json.dumps({'frame': encoded_frame}))
            else:
                print("Failed to encode image frame")
        else:
            print("No frame processed")
