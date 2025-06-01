# chats/serializers.py
from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email", "first_name", "last_name", "last_active"]
        read_only_fields = ["last_active"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Hash password before saving
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "message_body",
            "sent_at",
            "read",
        ]
        read_only_fields = ["message_id", "sent_at"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "created_at",
            "updated_at",
            "messages",
        ]
        read_only_fields = ["conversation_id", "created_at", "updated_at"]



class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    class Meta:
        model = Conversation
        fields = ["participant_ids"]

    def create(self, validated_data):
        participant_ids = validated_data.pop("participant_ids")
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participant_ids)
        return conversation


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["conversation", "message_body"]

    def create(self, validated_data):
        request = self.context.get("request")
        message = Message.objects.create(sender=request.user, **validated_data)
        return message
