from chat.mixins import ChatConsumerBase

class PrivateChatConsumer(ChatConsumerBase):
    def get_room_group_name(self, room_name):
        return f'private_chat_{room_name}'

class GroupChatConsumer(ChatConsumerBase):
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

    async def receive(self, text_data):
        logger.info(f"Received message: {text_data}")
        await self.send(text_data=text_data)
