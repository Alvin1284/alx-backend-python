from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Authenticated users
    - Participants of a conversation to access it
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        if not request.user.is_authenticated:
            return False

        # For list/create views, check if conversation_id is provided
        if view.action in ["list", "create"]:
            conversation_id = request.data.get(
                "conversation"
            ) or request.query_params.get("conversation")
            if conversation_id:
                from .models import Conversation

                try:
                    conversation = Conversation.objects.get(pk=conversation_id)
                    return request.user in conversation.participants.all()
                except Conversation.DoesNotExist:
                    return False
            return True  # Let has_object_permission handle it

        return True  # For other actions, let has_object_permission handle it

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant of the conversation
        if hasattr(obj, "conversation"):
            return request.user in obj.conversation.participants.all()
        elif hasattr(obj, "participants"):
            return request.user in obj.participants.all()
        return False


class IsMessageOwnerOrParticipant(permissions.BasePermission):
    """
    Allow only message owner or conversation participants to:
    - View, update, or delete messages
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read/write if user is sender, receiver, or conversation participant
        is_owner = obj.sender == request.user
        is_receiver = hasattr(obj, "receiver") and obj.receiver == request.user
        is_participant = request.user in obj.conversation.participants.all()

        return is_owner or is_receiver or is_participant
