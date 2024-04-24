from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model

User = get_user_model()

class WebSocketAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'cookie' in headers:
            session_key = headers[b'cookie'].decode().split(';')[0].split('=')[1]
            session = SessionMiddleware(get_response=None)
            scope['session'] = session.SessionStore(session_key)
            scope['user'] = await self.get_user(scope)
        return await super().__call__(scope, receive, send)

    async def get_user(self, scope):
        if 'session' in scope:
            session = scope['session']
            user_id = session.get('_auth_user_id')
            if user_id is not None:
                try:
                    return await User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    pass
        return AnonymousUser()
