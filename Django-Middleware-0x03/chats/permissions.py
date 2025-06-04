from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOrSender(permissions.BasePermission):
    """
    Allows access only if the user is a participant in a conversation
    or is the sender of a message.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        elif isinstance(obj, Message):
            return (
                request.user == obj.sender
                or request.user in obj.conversation.participants.all()
            )
        return False
