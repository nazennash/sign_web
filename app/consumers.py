import cv2
import base64
import json
import os
import numpy as np
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from .utils import generate_webcam_frames, generate_video_frames, process_image, download_youtube_video, preprocess_image, predict
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
            print(f"Starting {video_type} stream")
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
                self.thread = Thread(target=self.process_image, args=(image_full_path,))
                self.thread.start()
        elif command == 'stop':
            self.streaming = False
            print("Stopping stream")

    def stream_webcam(self):
        for frame in generate_webcam_frames():
            if not self.running or not self.streaming:
                break
            if frame is not None:
                print(f"Captured frame from webcam: {type(frame)}")  # Debug statement
                if not isinstance(frame, np.ndarray):
                    print("Error: frame is not a numpy array")
                    continue
                vector, hand_landmarks = preprocess_image(frame)
                predictions = []
                if vector is not None:
                    predicted_labels, predicted_probabilities = predict(vector)
                    predictions = [{"label": label, "probability": prob} for label, prob in zip(predicted_labels, predicted_probabilities)]
                print(f"Webcam predictions: {predictions}")
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    encoded_frame = base64.b64encode(buffer).decode('utf-8')
                    self.send(text_data=json.dumps({'frame': encoded_frame, 'predictions': predictions}))

    def stream_video(self, video_path):
        for frame in generate_video_frames(video_path):
            if not self.running or not self.streaming:
                break
            if frame is not None:
                print(f"Captured frame from video: {type(frame)}")  # Debug statement
                if not isinstance(frame, np.ndarray):
                    print("Error: frame is not a numpy array")
                    continue
                vector, hand_landmarks = preprocess_image(frame)
                predictions = []
                if vector is not None:
                    predicted_labels, predicted_probabilities = predict(vector)
                    predictions = [{"label": label, "probability": prob} for label, prob in zip(predicted_labels, predicted_probabilities)]
                print(f"Video predictions: {predictions}")
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    encoded_frame = base64.b64encode(buffer).decode('utf-8')
                    self.send(text_data=json.dumps({'frame': encoded_frame, 'predictions': predictions}))

    def process_image(self, image_path):
        frame = process_image(image_path)
        if not self.running or not self.streaming:
            return
        if frame is None or not isinstance(frame, np.ndarray):
            print("Error: frame is not a valid numpy array")
            return
        print(f"Processing image: {type(frame)}")  # Debug statement
        vector, hand_landmarks = preprocess_image(frame)
        predictions = []
        if vector is not None:
            predicted_labels, predicted_probabilities = predict(vector)
            predictions = [{"label": label, "probability": prob} for label, prob in zip(predicted_labels, predicted_probabilities)]
        print(f"Image predictions: {predictions}")
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            encoded_frame = base64.b64encode(buffer).decode('utf-8')
            self.send(text_data=json.dumps({'frame': encoded_frame, 'predictions': predictions}))
