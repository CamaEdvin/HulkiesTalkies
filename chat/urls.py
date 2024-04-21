from django.urls import path
from .views import NewRoomView, room_detail

urlpatterns = [
    path('new_room/', NewRoomView.as_view(), name='new_room'),
    path('room/<int:room_id>/', room_detail, name='room_detail'),
]