# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/video_feed/$', consumers.VideoConsumer.as_asgi()),
]
