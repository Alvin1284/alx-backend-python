# chats/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with additional fields.
    """
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_("User's email address")
    )
    password = models.CharField(
        _('password'),
        max_length=128,
        help_text=_("User's password (hashed)")
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=True,
        help_text=_("User's first name")
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True,
        help_text=_("User's last name")
    )
    
    # Additional fields can be added here
    last_active = models.DateTimeField(
        _('last active'),
        auto_now=True,
        help_text=_("When the user was last active")
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Conversation(models.Model):
    """
    Model representing a conversation between users.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        verbose_name=_('participants')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.conversation_id}"

class Message(models.Model):
    """
    Model representing a message in a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('conversation')
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('sender')
    )
    message_body = models.TextField(
        _('message body'),
        help_text=_("The content of the message")
    )
    sent_at = models.DateTimeField(
        _('sent at'),
        auto_now_add=True
    )
    read = models.BooleanField(
        _('read'),
        default=False,
        help_text=_("Whether the message has been read by the recipient")
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['sent_at']

    def __str__(self):
        return f"Message {self.message_id} in {self.conversation}"