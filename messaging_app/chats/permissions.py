from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Conversation


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to:
    - Send (POST), view (GET), update (PUT/PATCH), and delete (DELETE) messages
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Handle list/create actions
        if view.action in ["list", "create"]:
            conversation_id = request.data.get(
                "conversation"
            ) or request.query_params.get("conversation")
            if conversation_id:
                conversation = get_object_or_404(Conversation, pk=conversation_id)
                return conversation.participants.filter(pk=request.user.pk).exists()
            return True

        # Explicitly check for PUT, PATCH, DELETE methods
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return True  # Defer to has_object_permission

        return True

    def has_object_permission(self, request, view, obj):
        # Handle all methods (GET, PUT, PATCH, DELETE)
        if isinstance(obj, Conversation):
            return obj.participants.filter(pk=request.user.pk).exists()

        if hasattr(obj, "conversation"):
            return obj.conversation.participants.filter(pk=request.user.pk).exists()

        return False


class IsMessageOwnerOrParticipant(permissions.BasePermission):
    """
    Allow only message owner or conversation participants to:
    - View (GET), update (PUT/PATCH), or delete (DELETE) messages
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Explicitly handle all methods
        if request.method in permissions.SAFE_METHODS + ("PUT", "PATCH", "DELETE"):
            if obj.sender == request.user:
                return True
            if hasattr(obj, "receiver") and obj.receiver == request.user:
                return True
            return obj.conversation.participants.filter(pk=request.user.pk).exists()
        return False
