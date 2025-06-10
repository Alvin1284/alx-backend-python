from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions

# Explicitly import ValidationError from serializers
from rest_framework.serializers import ValidationError


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "status",
            "last_active",
        ]
        read_only_fields = ["last_active"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_type = serializers.CharField(source="get_message_type_display")
    is_own_message = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "message_body",
            "message_type",
            "sent_at",
            "read",
            "is_own_message",
        ]
        read_only_fields = ["message_id", "sent_at", "sender"]

    def get_is_own_message(self, obj):
        request = self.context.get("request")
        return request and request.user == obj.sender

    def validate_message_body(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Message cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError(
                "Message exceeds maximum length of 1000 characters"
            )
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "created_at",
            "updated_at",
            "messages",
            "last_message",
            "unread_count",
        ]
        read_only_fields = ["conversation_id", "created_at", "updated_at"]

    def get_messages(self, obj):
        messages = obj.messages.all().order_by("-sent_at")[:20]
        return MessageSerializer(messages, many=True, context=self.context).data

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.messages.filter(read=False).exclude(sender=request.user).count()
        return 0

    def validate(self, data):
        participants = data.get("participants", [])
        if len(participants) < 1:
            raise serializers.ValidationError(
                "Conversation must have at least one participant"
            )
        if len(participants) > 20:
            raise serializers.ValidationError("Cannot add more than 20 participants")
        return data


class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=True
    )

    class Meta:
        model = Conversation
        fields = ["participant_ids"]

    def validate_participant_ids(self, value):
        try:
            users = User.objects.filter(user_id__in=value)
            if len(users) != len(value):
                raise serializers.ValidationError("One or more user IDs are invalid")
            return users
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid user ID format")

    def create(self, validated_data):
        participants = validated_data.pop("participant_ids")
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        return conversation


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Authenticated users
    - Participants of a conversation to access it
    - Explicit handling of PUT, PATCH, DELETE methods
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

        # Explicit check for PUT, PATCH, DELETE
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return True  # Delegate to has_object_permission

        return True

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant of the conversation
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            if hasattr(obj, "conversation"):
                return request.user in obj.conversation.participants.all()
            elif hasattr(obj, "participants"):
                return request.user in obj.participants.all()

        # For PUT, PATCH, DELETE - only allow if user is participant
        elif request.method in ["PUT", "PATCH", "DELETE"]:
            if hasattr(obj, "conversation"):
                return request.user in obj.conversation.participants.all()
            elif hasattr(obj, "participants"):
                return request.user in obj.participants.all()

        return False


class IsMessageOwnerOrParticipant(permissions.BasePermission):
    """
    Allow only message owner or conversation participants to:
    - View, update, or delete messages
    - Explicit handling of PUT, PATCH, DELETE methods
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.sender == request.user
                or (hasattr(obj, "receiver") and obj.receiver == request.user)
                or request.user in obj.conversation.participants.all()
            )

        # For PUT, PATCH - only allow message owner
        elif request.method in ["PUT", "PATCH"]:
            return obj.sender == request.user

        # For DELETE - allow message owner or conversation participants
        elif request.method == "DELETE":
            return (
                obj.sender == request.user
                or request.user in obj.conversation.participants.all()
            )

        return False
