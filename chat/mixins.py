from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import User

class ChatConsumerBase(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        print("AAAA")
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = self.get_room_group_name()

            print("self.room_name:", self.room_name)
            print("self.room_group_name:", self.room_group_name)

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        except Exception as e:
            print("Error in connect:", e)   


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_status = text_data_json.get('status', 'sent')
        username = text_data_json['username']

        print("message: ", message)
        print("message_status: ", message_status)
        print("username: ", username)


        # Save message to database
        await sync_to_async(self.save_message)(message, message_status, username)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'message_status': message_status,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        print("message: ", message)
        print("username: ", username)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    def save_message(self, message, username):
        message = Message.objects.create(content=message, sender=User.objects.get(username=username))
        print("message: ", message)

    def get_room_group_name(self):
        return f'chat_'