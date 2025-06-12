# chats/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Conversation, Message
from .permissions import IsParticipantOfConversation, IsMessageOwnerOrParticipant, IsParticipantOrSender, IsAuthenticated
from django.http import Http404

from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
)
from .filters import MessageFilter, ConversationFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination


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
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrSender]
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
    serializer_class = MessageSerializer
    permission_classes = [
        IsAuthenticated,
        IsParticipantOfConversation,
        IsMessageOwnerOrParticipant,
    ]
    pagination_class = CustomMessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        queryset = Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('conversation', 'sender', 'recipient').order_by('-timestamp')

        # Apply additional filtering if needed
        return queryset

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation")
        if not conversation_id:
            return Response(
                {"detail": "Conversation ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            conversation = Conversation.objects.get(pk=conversation_id)
            if not conversation.participants.filter(pk=request.user.pk).exists():
                return Response(
                    {"detail": "You are not a participant of this conversation"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Conversation.DoesNotExist:
            raise Http404("Conversation does not exist")

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.sender != request.user:
                return Response(
                    {"detail": "You can only delete your own messages"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return super().destroy(request, *args, **kwargs)
        except Http404:
            return Response(
                {"detail": "Message not found"}, status=status.HTTP_404_NOT_FOUND
            )
