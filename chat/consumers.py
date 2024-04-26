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
from channels.auth import login
logger = logging.getLogger(__name__)



from django.contrib.auth import get_user_model

User = get_user_model()

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            print("self.user: ", self.user)
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept(subprotocol='websocket')
            print("self.channel_layer: ", self.channel_layer)
            logger.info(f"WebSocket connection established for room {self.room_name} ({self.room_type})")
        else:
            # Perform login using the session ID if available
            session_key = self.scope.get("session", {}).session_key
            print("session_key: ", session_key)
            if session_key:
                session = SessionStore(session_key=session_key)
                print("session: ", session)
                user_id = session.get('_auth_user_id')
                print("user_id: ", user_id)
                if user_id:
                    user = await self.get_user(user_id)
                    print("user: ", user)
                    if user:
                        await database_sync_to_async(login)(self.scope, user)
                        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
                        await self.accept(subprotocol='websocket')
                        logger.info(f"WebSocket connection established for room {self.room_name} ({self.room_type})")
                else:
                    await self.close()
            else:
                await self.close()


    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        print("disconnect")
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for room {self.room_name}")

    async def receive(self, text_data):
        print("receive: ", receive)
        print("self.scope: ", self.scope)
        await login(self.scope, user)
        # save the session (if the session backend does not access the db you can use `sync_to_async`)
        await database_sync_to_async(self.scope["session"].save)()


    """async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print("text_data_json: ", text_data_json)
        message = text_data_json['message']
        print("message: ", message)
        username = self.scope['user'].username 
        print("username: ", username)
        
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
        """

       

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        print("message: ", message)
        print("username: ", username)

        # Send the message to the client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
        logger.info(f"Message sent to room {self.room_name}: {message}")

    async def save_message(self, message, username):
        sender = User.objects.get(username=username)
        print("sender: ", sender)
        models.Message.objects.create(content=message, sender=sender, room=self.room)
        logger.info(f"Message saved in database for room {self.room_name}: {message}")


    @database_sync_to_async
    def get_room(self, name):
        print("get_room")
        try:
            return models.Room.objects.get(name=name)
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

    async def receive(self, text_data):
        try:
            if text_data:
                logger.info(f"Received message: {text_data}")
                await self.send(text_data=text_data)
        except Exception as e:
            logger.error(f"Error in receiving message: {e}")



