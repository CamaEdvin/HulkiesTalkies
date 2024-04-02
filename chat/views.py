from django.shortcuts import render
from django.contrib.auth.models import User
from django.views import View
from django.shortcuts import redirect
from chat import models


class NewRoomView(View):
    def get(self, request):
        users = User.objects.all()
        context = {'users': users}
        return render(request, 'chat.html', context)

    def post(self, request):
        user_ids = request.POST.getlist('recipients')
        print("user_ids: ", user_ids)

        usernames = [User.objects.get(id=user_id).username for user_id in user_ids]
        room_name = ', '.join(usernames)
        print("room_name: ", room_name)

        if len(user_ids) == 1:
            room_type = 'private'
        elif len(user_ids) > 1:
            room_type = 'group'

        print("room_type: ", room_type)

        room = models.Room.objects.create(name=room_name, room_type=room_type)
        room_member = models.RoomMember.objects.create(room=room)

        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            print("user: ", user)
            room_member.users.add(user)
            print("room_member.users: ", room_member.users)


        context = {
            'room_name': room_name,
            'room_type': room_type,
        }

        return render(request, 'chat/chat.html', context)

def dashboard(request):
    users = User.objects.all()
    rooms = models.Room.objects.all()
    messages = []

    for room in rooms:
        latest_message = models.Message.objects.filter(room=room).order_by('-timestamp').first()
        messages.append({'room': room, 'latest_message': latest_message})


    context = {
        'users': users,
        'messages': messages
        }

    return render(request, 'dashboard.html', context)