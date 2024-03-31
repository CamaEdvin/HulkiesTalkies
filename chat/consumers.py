from chat import mixins
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer
import json


class PrivateChatConsumer(mixins.ChatConsumerBase):
    def get_room_group_name(self, name):
        return f'private_chat_{name}'

class GroupChatConsumer(mixins.ChatConsumerBase):
    def get_room_group_name(self, name):
        return f'group_chat_{name}'

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



