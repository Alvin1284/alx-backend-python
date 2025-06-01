from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 
            'email', 
            'first_name', 
            'last_name', 
            'full_name',
            'status',
            'last_active'
        ]
        read_only_fields = ['last_active']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_type = serializers.CharField(source='get_message_type_display')
    is_own_message = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'sender',
            'message_body',
            'message_type',
            'sent_at',
            'read',
            'is_own_message'
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender']

    def get_is_own_message(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.sender

    def validate_message_body(self, value):
        if len(value.strip()) == 0:
            raise ValidationError("Message cannot be empty")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'created_at',
            'updated_at',
            'messages',
            'last_message',
            'unread_count'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('-sent_at')[:20]  # Get last 20 messages
        return MessageSerializer(messages, many=True, context=self.context).data

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(read=False).exclude(sender=request.user).count()
        return 0

    def validate(self, data):
        participants = data.get('participants', [])
        if len(participants) < 1:
            raise ValidationError("Conversation must have at least one participant")
        return data

class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Conversation
        fields = ['participant_ids']

    def validate_participant_ids(self, value):
        try:
            users = User.objects.filter(user_id__in=value)
            if len(users) != len(value):
                raise ValidationError("One or more user IDs are invalid")
            return users
        except DjangoValidationError:
            raise ValidationError("Invalid user ID format")

    def create(self, validated_data):
        participants = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        return conversation