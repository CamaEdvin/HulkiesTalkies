from chat.mixins import ChatConsumerBase

class PrivateChatConsumer(ChatConsumerBase):
    def get_room_group_name(self, room_name):
        return f'private_chat_{room_name}'

class GroupChatConsumer(ChatConsumerBase):
    def get_room_group_name(self, room_name):
        return f'group_chat_{room_name}'
    

from channels.generic.websocket import AsyncWebsocketConsumer

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        await self.send(text_data=text_data)