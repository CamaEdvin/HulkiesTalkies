from django.urls import path
from .views import NewRoomView, RoomDetailView

urlpatterns = [
    path('new_room/', NewRoomView.as_view(), name='new_room'),
    path('room/<int:room_id>/', RoomDetailView.as_view(), name='room_detail'),
]