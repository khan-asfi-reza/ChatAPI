from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from Accounts.serializer import ProfileRetrieveSerializer
from Accounts.views import ProfilePagination
from Chat.models import Inbox, ChatMessage
from Chat.serializers import InboxSerializer, MessageSerializer
from Accounts.models import Profile
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
User = get_user_model()


class InboxDeleteView(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'

    @action(methods='delete', detail=False)
    def destroy(self, request, *args, **kwargs):
        try:
            inbox = Inbox.objects.get(user=request.user, second__username=self.kwargs.get('username'))
            inbox.delete()
            return Response({'msg': 'Inbox deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Inbox.DoesNotExist:
            return Response({'error': 'Inbox does not exists'}, status=status.HTTP_400_BAD_REQUEST)


class UserInboxView(ModelViewSet):
    serializer_class = ProfileRetrieveSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(methods='get', detail=True)
    def retrieve(self, request, *args, **kwargs):
        try:
            user_profile = Profile.objects.get(user__name=self.kwargs.get('user'))
            serializer = self.serializer_class(instance=user_profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)


class InboxMessageView(ModelViewSet):
    serializer_class = MessageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = ProfilePagination

    def get_queryset(self):
        try:
            other_user = User.objects.get(name=self.kwargs.get('username'))
            try:
                inbox = Inbox.objects.get(user=self.request.user, second=other_user)
                return ChatMessage.objects.filter(inbox=inbox).order_by('-timestamp')
            except Inbox.DoesNotExist:
                return []

        except User.DoesNotExist:
            return []


class InboxListView(ModelViewSet):
    serializer_class = InboxSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = ProfilePagination

    def get_queryset(self):
        return Inbox.objects.filter(user=self.request.user).order_by('-updated')

