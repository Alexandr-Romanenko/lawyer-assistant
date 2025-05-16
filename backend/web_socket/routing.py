# from django.urls import path
# from web_socket.consumers import ProgressConsumer
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/progress/$', consumers.ProgressConsumer.as_asgi()),
]
# websocket_urlpatterns = [
#     path("ws/progress/", ProgressConsumer.as_asgi()),
# ]
