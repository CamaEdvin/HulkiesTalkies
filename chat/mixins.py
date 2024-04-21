from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import User
from chat import models
from channels.db import database_sync_to_async

class ChatConsumerBase(AsyncWebsocketConsumer):
    #print("START")
    async def connect(self):
        #print("START connect")
        self.room = self.scope['url_route']['kwargs']['room_name']

        #print("self.room: ", self.room)
        self.room_group_name = self.get_room_group_name(self.room)



        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        await self.save_message(message, username)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def save_message(self, message, username):
        sender = User.objects.get(username=username)
        room = models.Room.objects.get(name=self.room)
        models.Message.objects.create(content=message, sender=sender, room=room)

    def get_room_group_name(self, room):
        return f'chat_{room}'

