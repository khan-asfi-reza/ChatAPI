from urllib import parse

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from Accounts.models import Profile
from Chat.models import Thread, Inbox, ChatMessage
from Chat.serializers import MessageSerializer

User = get_user_model()


# Returns user by validating Token
class TokenAuth(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user(self):
        scope = self.scope
        try:
            # Parse the scope and gets the token
            query = parse.parse_qs(scope['query_string'].decode("utf-8"))['token'][0]
            if query:
                token = Token.objects.get(key=query)
                # Returns token user
                return token.user

        except Token.DoesNotExist:
            return None


# Determines users Online/Offline Activity
class OnlineOfflineConsumer(AsyncJsonWebsocketConsumer, TokenAuth):

    # Connects Websocket
    async def connect(self):
        # Accepts the connection
        await self.accept()
        # Get the request user
        user = await self.get_user()
        # If user is authenticated
        if user is not None:
            # Update user Status to Online
            await self.channel_layer.group_add("online_users", self.channel_name)
            await self.update_user_status(user, True)

    async def disconnect(self, code):
        # Discard
        await self.channel_layer.group_discard("online_users", self.channel_name)
        user = await self.get_user()
        if user is not None:
            # Update user status to Offline
            await self.update_user_status(user, False)

    async def user_update(self, event):
        await self.send_json(event)

    @database_sync_to_async
    def update_user_status(self, user, status):
        # Get profile and update status
        profile = Profile.objects.get(user=user)
        profile.online = status
        profile.save()
        return profile


# User Inbox Consumer
class InboxConsumer(AsyncJsonWebsocketConsumer, TokenAuth):
    # Accepts connection
    async def connect(self):
        user = await self.get_user()
        await self.channel_layer.group_add(f"inbox_{user.username}", self.channel_name)
        await self.accept()

    # Disconnects
    async def disconnect(self, code):
        user = await self.get_user()
        await self.channel_layer.group_discard(f"inbox_{user.username}", self.channel_name)

    # Send updated inbox data
    async def update_inbox(self, event):
        await self.send_json(event["content"])


class MessageConsumer(AsyncJsonWebsocketConsumer, TokenAuth):

    # Connects To Message Consumer
    async def connect(self):
        user = await self.get_user()
        if user is not None:
            second_user = self.scope['url_route']['kwargs']['username']
            thread = await self.get_thread(user, second_user)
            await self.read_user_inbox(user, second_user)
            # Add to channel layer
            await self.channel_layer.group_add(f"thread_{thread.id}", self.channel_name)
            await self.accept()

    # Disconnects
    async def disconnect(self, code):
        user = await self.get_user()
        second_user = self.scope['url_route']['kwargs']['username']
        thread = await self.get_thread(user, second_user)
        await self.channel_layer.group_discard(f"thread_{thread.id}", self.channel_name)
        await self.accept()

    # Receives message from socket
    async def receive_json(self, content, **kwargs):
        user = await self.get_user()
        second_user = self.scope['url_route']['kwargs']['username']
        thread = await self.get_thread(user, second_user)
        message = content["message"]
        inboxes = await self.get_inbox(user, second_user)
        msg = await self.create_msg(user=user, other_user=second_user, thread=thread, msg=message, inbox=inboxes)
        await self.read_user_inbox(user, second_user)
        data = MessageSerializer(instance=msg).data
        await self.channel_layer.group_send(f'thread_{thread.id}',
                                            {
                                                'type': 'send_msg',
                                                'content': data
                                            })
    # Broadcast to channel layer
    async def send_msg(self, event):
        await self.send_json(event['content'])

    @database_sync_to_async
    def get_thread(self, user, other_user):
        return Thread.objects.get_or_new(user, other_user)[0]

    @database_sync_to_async
    def get_inbox(self, user, other_user):
        try:
            second_user = User.objects.get(username=other_user)
            user_inbox, created = Inbox.objects.get_or_create(user=user, second=second_user)
            other_user_inbox, created = Inbox.objects.get_or_create(user=second_user, second=user)
            return [user_inbox, other_user_inbox]
        except User.DoesNotExist:
            return []

    @database_sync_to_async
    def read_user_inbox(self, user, other_user):
        second_user = User.objects.get(username=other_user)
        Inbox.objects.read_inbox(user, second_user)

    @database_sync_to_async
    def create_msg(self, user, other_user, msg, inbox, thread, ):
        second_user = User.objects.get(username=other_user)
        cm = ChatMessage.objects.create(user=user, message=msg, thread=thread, receiver=second_user)
        for each in inbox:
            cm.inbox.add(each)
            cm.save()
        return cm
