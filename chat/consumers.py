from chat import mixins
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer
import json
from .models import Message
from django.contrib.auth.models import User

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'private_chat_{self.room_name}'

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

    def save_message(self, message, message_status, username):
        message = Message.objects.create(content=message, sender=User.objects.get(username=username))
        print("message: ", message)


class GroupChatConsumer(mixins.ChatConsumerBase):
    def get_room_group_name(self, room_name):
        return f'group_chat_{room_name}'

import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info("WebSocket connection established.")

    async def disconnect(self, close_code):
        logger.info("WebSocket connection closed.")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                logger.info(f"Received message: {text_data}")
                await self.send(text_data=text_data)
        except Exception as e:
            logger.error(f"Error in receiving message: {e}")


class HelloWorldConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data="Hello, world!")


class PingConsumer(AsyncConsumer):
    async def websocket_connect(self, message):
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, message):
        await asyncio.sleep(1)
        await self.send({
            "type": "websocket.send",
            "text": "pong",
        })
