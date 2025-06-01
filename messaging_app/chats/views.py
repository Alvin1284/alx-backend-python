# chats/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)


class MessageFilter(filters.FilterSet):
    conversation = filters.UUIDFilter(field_name="conversation__conversation_id")
    sender = filters.UUIDFilter(field_name="sender__user_id")
    read = filters.BooleanFilter(field_name="read")
    after_date = filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")
    before_date = filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ["conversation", "sender", "read", "after_date", "before_date"]


class ConversationFilter(filters.FilterSet):
    participant = filters.UUIDFilter(field_name="participants__user_id")
    after_date = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    before_date = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    has_unread = filters.BooleanFilter(method="filter_has_unread")

    class Meta:
        model = Conversation
        fields = ["participant", "after_date", "before_date", "has_unread"]

    def filter_has_unread(self, queryset, name, value):
        if value:
            return (
                queryset.filter(messages__read=False)
                .exclude(messages__sender=self.request.user)
                .distinct()
            )
        return queryset


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ConversationFilter

    def get_serializer_class(self):
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer

    def get_queryset(self):
        # Only show conversations the user is part of
        queryset = self.queryset.filter(participants=self.request.user)
        return queryset.prefetch_related("participants", "messages")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        # Add current user to participants if not already included
        if request.user not in conversation.participants.all():
            conversation.participants.add(request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all().order_by("-sent_at")
        page = self.paginate_queryset(messages)

        if page is not None:
            serializer = MessageSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(
            messages, many=True, context={"request": request}
        )
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MessageFilter

    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        # Only show messages in conversations the user is part of
        queryset = self.queryset.filter(
            conversation__participants=self.request.user
        ).order_by("-sent_at")
        return queryset.select_related("sender", "conversation")

    def perform_create(self, serializer):
        # Automatically set the sender to the current user
        serializer.save(sender=self.request.user)
