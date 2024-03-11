from django.urls import path
from .views import NewRoomView

urlpatterns = [
    path('new_room/', NewRoomView.as_view(), name='new_room'),
]