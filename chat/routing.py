from django.urls import re_path
from chat import consumers


websocket_urlpatterns = [
    re_path(r'private/(?P<room_name>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
    re_path(r'group/(?P<room_name>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
    re_path(r'test/$', consumers.TestConsumer.as_asgi()),
]

