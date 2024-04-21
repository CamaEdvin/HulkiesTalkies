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
        jwt_token = self.scope['headers']['authorization'][1].decode('utf-8').split()[1]
        print("jwt_token: ", jwt_token)
        
        # Authenticate the user using Simple JWT's JWTAuthentication
        jwt_authentication = JWTAuthentication()
        try:
            user, _ = jwt_authentication.authenticate(jwt_token)
            # Set the authenticated user in the consumer's scope
            self.scope['user'] = user
        except Exception as e:
            # Handle authentication failure
            print("Authentication error:", e)
            await self.close()
            return
        
        try:
            self.room = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = self.get_room_group_name(self.room)
        except KeyError:
            logger.error("Room name not provided")
            await self.close()
            return

        # Extract the user from the session
        user = self.get_user_from_session()
        print("user: ", user)

        if user is None:
            logger.error("User not found in session")
            await self.close()
            return

        # Set the user in the scope
        self.scope['user'] = user
        print("self.scope: ", self.scope)

        # Add the channel to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()
        logger.info(f"WebSocket connection established for room {self.room}")

    async def disconnect(self, close_code):
        # Remove the channel from the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for room {self.room}")

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username  # Assuming you have authentication set up
        logger.info(f"Received message in room {self.room} from {username}: {message}")

        await self.save_message(message, username)

        # Send the message to the room group
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

        # Send the message to the client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
        logger.info(f"Message sent to room {self.room}: {message}")

    async def save_message(self, message, username):
        sender = User.objects.get(username=username)
        # Assuming you have a Message model to save messages
        # Replace Message.objects.create(...) with your actual save logic
        # models.Message.objects.create(content=message, sender=sender, room=self.room)
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

    def get_room_group_name(self, room):
        return f'chat_{room}'

"""class GroupChatConsumer(mixins.ChatConsumerBase):
    def get_room_group_name(self, name):
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


