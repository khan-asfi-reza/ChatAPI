from rest_framework import serializers
from Accounts.serializer import UserRetrieveSerializer
from Accounts.models import Profile
from Accounts.serializer import ProfileRetrieveSerializer
from .models import Inbox, ChatMessage, Attachment, Thread


class InboxSerializer(serializers.ModelSerializer):
    user = UserRetrieveSerializer(many=False, read_only=True)
    second = serializers.SerializerMethodField()
    request = serializers.SerializerMethodField()
    last_message_from = UserRetrieveSerializer(many=False, read_only=True)

    def get_second(self, obj):
        if 'request' in self.context:
            profile_serializer = ProfileRetrieveSerializer(instance=Profile.objects.get(user=obj.second),
                                                           context={'request': self.context['request']})
            return profile_serializer.data
        else:
            profile_serializer = ProfileRetrieveSerializer(instance=Profile.objects.get(user=obj.second))
            return profile_serializer.data

    def get_request(self, obj):
        if 'request' in self.context:
            return True
        else:
            return False

    class Meta:
        model = Inbox
        fields = ['id', 'user', 'second', 'last_message', 'timestamp', 'updated', 'request', 'read','last_message_from']


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ['id']


class MessageSerializer(serializers.ModelSerializer):
    user = UserRetrieveSerializer(many=False, read_only=True)
    receiver = UserRetrieveSerializer(many=False, read_only=True)
    attachment = AttachmentSerializer(many=False, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'receiver', 'message', 'timestamp', 'thread', 'attachment']
