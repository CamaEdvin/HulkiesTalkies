from chat import mixins
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer, WebsocketConsumer
import json
from chat import models
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication

import logging

logger = logging.getLogger(__name__)



class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        jwt_token = None
        print("self.scope['headers']: ", self.scope['headers'])
        print("self.scope['query_string'].decode('utf-8'): ", self.scope['query_string'].decode('utf-8'))
        room = await self.get_room(room_name)
        if room is None:
            logger.error(f"Room '{room_name}' not found")
            await self.close()
            return

        # Your authentication logic here, if needed
        # Example: check for a query parameter in the URL
        jwt_token = self.scope['query_string'].decode('utf-8')
        print("jwt_token: ", jwt_token)
        if not jwt_token:
            logger.error("JWT token not provided in query parameters")
            await self.close()
            return

        # Your room fetching logic here
        room = await self.get_room(room_name)
        if room is None:
            logger.error(f"Room '{room_name}' not found")
            await self.close()
            return

        # Add the channel to the room group using the room's name
        await self.channel_layer.group_add(
            room_name,
            self.channel_name
        )

        self.room_name = room_name

        # Accept the WebSocket connection
        await self.accept(subprotocol='websocket')
        logger.info(f"WebSocket connection established for room {room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for room {self.room_name}")

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username  # Assuming you have authentication set up
        logger.info(f"Received message in room {self.room_name} from {username}: {message}")

        await self.save_message(message, username)

        # Send the message to the room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send the message to the client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
        logger.info(f"Message sent to room {self.room_name}: {message}")

    async def save_message(self, message, username):
        sender = User.objects.get(username=username)
        models.Message.objects.create(content=message, sender=sender, room=self.room)
        logger.info(f"Message saved in database for room {self.room}: {message}")

    def get_user_from_session(self):
        if hasattr(self.scope['session'], '_session_cache'):
            # For Django 3.1+
            user_id = self.scope['session']._session_cache.get('_auth_user_id')
        else:
            user_id = self.scope['session'].get('_auth_user_id')
        if user_id:
            return User.objects.get(id=user_id)
        return None

    @database_sync_to_async
    def get_room(self, room_name):
        print("room_name: ", room_name)
        try:
            return models.Room.objects.get(name=room_name)
        except models.Room.DoesNotExist:
            return None

"""class GroupChatConsumer(mixins.ChatConsumerBase):
    def get_name(self, name):
        return f'group_chat_{name}'"""

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



