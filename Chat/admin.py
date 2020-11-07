from django.contrib import admin

from .models import Thread, ChatMessage, Inbox


class ChatMessageAdmin(admin.TabularInline):
    model = ChatMessage


class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessageAdmin]
    list_display = ('first', 'second', 'id', 'timestamp', 'updated')
    readonly_fields = ('updated', 'timestamp')

    class Meta:
        model = Thread


class InboxAdmin(admin.ModelAdmin):
    list_display = ('user', 'second', 'id', 'timestamp', 'updated')
    fieldsets = (
        (None, {'fields': ('user', 'second', 'last_message', 'read')}),

    )
    readonly_fields = ('updated', 'timestamp')

    class Meta:
        model = Inbox


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Inbox, InboxAdmin)
