from django.urls import re_path
from chat import consumers


websocket_urlpatterns = [
    re_path(r'ws/(?P<room_type>\w+)/(?P<room_name>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
    #re_path(r'ws/(?P<room_type>\w+)/(?P<room_name>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
]

