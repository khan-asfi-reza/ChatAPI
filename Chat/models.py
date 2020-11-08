from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils import FieldTracker
from Accounts.models import user_directory_path, Profile
from encrypted_fields import fields
channel_layer = get_channel_layer()

User = get_user_model()


# Thread Manager -> Manages thread object operations
class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_name):
        # get_or_create -> Finds existing thread or creates new one
        username = user.username
        if username == other_name:
            return None
        qlookup1 = Q(first__username=username) & Q(second__username=other_name)
        qlookup2 = Q(first__username=other_name) & Q(second__username=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            try:
                user2 = User.objects.get(username=other_name)
            except User.DoesNotExist:
                return None, False
            if user != user2:
                obj = self.model(
                    first=user,
                    second=user2
                )
                obj.save()
                return obj, True
            return None, False


# Each thread consist of 2 users
class Thread(models.Model):
    first = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_thread_first')
    second = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first', 'second']

    @property
    def room_group_name(self):
        return f'chat_{self.id}'

    def __str__(self):
        return f"{self.first} - {self.second} Thread - ID: ${self.pk}"


class InboxManager(models.Manager):
    def set_inbox(self, user, other_user, msg, read=False):
        inbox_object, created_1 = self.get_or_create(user=user, second=other_user)
        inbox_object.last_message = msg
        inbox_object.read = read
        inbox_object.last_message_from = user
        inbox_object.save()
        from .serializers import InboxSerializer
        ib1 = InboxSerializer(instance=inbox_object).data
        async_to_sync(channel_layer.group_send)(f"inbox_{inbox_object.user.username}",
                                                {"type": "update_inbox",
                                                 "content": {
                                                     'type': 'inbox_update',
                                                     'payload': ib1
                                                 }})

        return None

    def read_inbox(self, user, other_user):
        inbox = self.get_queryset().filter(user=user, second=other_user)
        if inbox.count() == 1:
            inbox_obj = inbox.first()
            inbox_obj.read = True
            inbox_obj.save()
            from .serializers import InboxSerializer
            inbox_data = InboxSerializer(instance=inbox_obj).data
            async_to_sync(channel_layer.group_send)(f"inbox_{inbox_obj.user.username}",
                                                    {"type": "update_inbox",
                                                     "content": {
                                                         'type': 'read_update',
                                                         'payload': inbox_data
                                                     }})

            return None


class Inbox(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_user')
    second = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_second_user')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_message = fields.EncryptedTextField(blank=True, )
    last_message_from = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='last_message_user',blank=True, null=True)
    read = models.BooleanField(default=False)

    tracker = FieldTracker()
    objects = InboxManager()

    class Meta:
        unique_together = ['user', 'second']
        verbose_name = 'User Inbox'
        verbose_name_plural = 'User Inbox'

    def __str__(self):
        return f"{self.user} - {self.second} Inbox - ID: {self.pk}"


class Attachment(models.Model):
    file = models.FileField(upload_to=user_directory_path)


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, verbose_name='sender', related_name='message_sender',
                             on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='message_receiver', verbose_name='receiver',
                                 on_delete=models.CASCADE)
    inbox = models.ManyToManyField(to=Inbox, blank=True)
    message = fields.EncryptedTextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.ForeignKey(to=Attachment, on_delete=models.SET_NULL, null=True, blank=True)


@receiver(post_save, sender=ChatMessage)
def update_inbox(sender, instance, created, **kwargs):
    if created:
        Inbox.objects.set_inbox(user=instance.user, other_user=instance.receiver, msg=instance.message, read=True)
        Inbox.objects.set_inbox(other_user=instance.user, user=instance.receiver, msg=instance.message, read=False)
        return None
