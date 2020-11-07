from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

# from Chat.consumers import OnlineOfflineConsumer, InboxConsumer, MessageConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            # path('ws/status/', OnlineOfflineConsumer),
            # path('ws/inbox/', InboxConsumer),
            # path('ws/chat/<username>/', MessageConsumer),
        ])
    ),
})
