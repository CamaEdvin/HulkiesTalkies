from django.urls import path, re_path
from .consumers import PrivateChatConsumer, GroupChatConsumer, TestConsumer

websocket_urlpatterns = [
    re_path(r'ws/private/(?P<room_name>\w+)/$', PrivateChatConsumer.as_asgi()),
    re_path(r'ws/group/(?P<room_name>\w+)/$', GroupChatConsumer.as_asgi()),
    re_path(r'ws/test/$', TestConsumer.as_asgi()),
]