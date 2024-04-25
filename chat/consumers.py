from chat import mixins
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer, WebsocketConsumer
import json
from chat import models
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import logging
from django.contrib.sessions.middleware import SessionMiddleware
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.middleware import AuthenticationMiddleware
from urllib.parse import parse_qs
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
logger = logging.getLogger(__name__)



from django.contrib.auth import get_user_model

User = get_user_model()






class PrivateChatConsumer(WebsocketConsumer):
    def connect(self):
        self.username = "Anonymous"
        self.accept(subprotocol='websocket')
        # Continue with room setup and WebSocket connection acceptance
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        print("self.room_name: ", self.room_name)
        self.room_type = self.scope["url_route"]["kwargs"]["room_type"]
        print("self.room_type: ", self.room_type)
        self.room_group_name = "chat_%s" % self.room_name
        print("self.room_group_name: ", self.room_group_name)
        room = self.get_room(self.room_name)
        print("room: ", room)
        if room is None:
            logger.error(f"Room '{self.room_name}' not found")
            self.close()
            return

        if self.room_type == 'private':
            self.channel_layer.group_add(
                f"private_{self.room_name}",
                self.channel_name
            )
        elif self.room_type == 'group':
            self.channel_layer.group_add(
                f"group_{self.room_name}",
                self.channel_name
            )
        else:
            logger.error(f"Invalid room type: {self.room_type}")
            self.close()
            return

        
        logger.info(f"WebSocket connection established for room {self.room_name} ({self.room_type})")


    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def disconnect(self, close_code):
        print("disconnect")
        self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for room {self.room_name}")


    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print("text_data_json: ", text_data_json)
        message = text_data_json['message']
        print("message: ", message)
        username = self.scope['user'].username 
        print("username: ", username)
        
        logger.info(f"Received message in room {self.room_name} from {username}: {message}")

        self.save_message(message, username)

        # Send the message to the room group
        self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    def chat_message(self, event):
        message = event['message']
        username = event['username']
        print("message: ", message)
        print("username: ", username)

        # Send the message to the client
        self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
        logger.info(f"Message sent to room {self.room_name}: {message}")

    def save_message(self, message, username):
        sender = User.objects.get(username=username)
        print("sender: ", sender)
        models.Message.objects.create(content=message, sender=sender, room=self.room)
        logger.info(f"Message saved in database for room {self.room_name}: {message}")


    @database_sync_to_async
    def get_room(self, name):
        print("get_room")
        try:
            room = models.Room.objects.get(name=name)
            print("room: ", room)
            return room
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



