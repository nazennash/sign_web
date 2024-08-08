# consumers.py
import cv2
import base64
from channels.generic.websocket import WebsocketConsumer
import json
from .utils import generate_webcam_frames

class VideoConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket connection established")

    def disconnect(self, close_code):
        print("WebSocket connection closed")

    def receive(self, text_data):
        print("WebSocket message received")
        for frame in generate_webcam_frames():
            if frame is not None:
                encoded_frame = base64.b64encode(frame).decode('utf-8')
                self.send(text_data=json.dumps({
                    'frame': encoded_frame
                }))
            else:
                print("No frame captured")
