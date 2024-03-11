from django.test import TestCase
import asyncio
import websockets
import json

class ChatTestCase(TestCase):
    async def send_message(self, uri, room_type, room_name, message, username):
        async with websockets.connect(uri) as websocket:
            # Construct message data
            message_data = {
                'message': message,
                'username': username,
                'room_type': room_type,
                'room_name': room_name
            }
            # Send message
            await websocket.send(json.dumps(message_data))
            print(f"Sent message: {message}")

    async def receive_message(self, uri):
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")

    def test_chat_functionality(self):
        # WebSocket URI
        uri = "ws://0.0.0.0:8001/ws/private/test-room/"
        asyncio.run(self.send_and_receive_messages(uri))

    async def send_and_receive_messages(self, uri):
        await asyncio.gather(
            self.send_message(uri, 'private', 'test-room', 'Hello, world!', 'test_user'),
            self.receive_message(uri)
        )
