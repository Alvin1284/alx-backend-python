# messaging_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """

    phone_number = models.CharField(
        _("phone number"), max_length=20, blank=True, null=True, unique=True
    )
    profile_picture = models.ImageField(
        _("profile picture"), upload_to="profile_pics/", blank=True, null=True
    )
    status = models.CharField(
        _("status"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("User's current status/mood"),
    )
    last_active = models.DateTimeField(
        _("last active"), auto_now=True, help_text=_("When the user was last active")
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username


class Conversation(models.Model):
    """
    Model representing a conversation between users.
    """

    participants = models.ManyToManyField(
        User, related_name="conversations", verbose_name=_("participants")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    is_group = models.BooleanField(
        _("is group conversation"),
        default=False,
        help_text=_("Whether this is a group conversation"),
    )
    name = models.CharField(
        _("name"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Name of the conversation (optional, mainly for groups)"),
    )

    class Meta:
        verbose_name = _("conversation")
        verbose_name_plural = _("conversations")
        ordering = ["-updated_at"]

    def __str__(self):
        if self.name:
            return self.name
        participants = self.participants.all()[:3]
        names = [user.username for user in participants]
        if self.participants.count() > 3:
            names.append("...")
        return f"Conversation between {', '.join(names)}"


class Message(models.Model):
    """
    Model representing a message in a conversation.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("conversation"),
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name=_("sender"),
    )
    content = models.TextField(_("content"), help_text=_("The message content"))
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
    read = models.BooleanField(
        _("read"),
        default=False,
        help_text=_("Whether the message has been read by the recipient"),
    )
    # For message types (text, image, etc.)
    MESSAGE_TYPE_TEXT = "text"
    MESSAGE_TYPE_IMAGE = "image"
    MESSAGE_TYPE_VIDEO = "video"
    MESSAGE_TYPE_FILE = "file"

    MESSAGE_TYPE_CHOICES = [
        (MESSAGE_TYPE_TEXT, _("Text")),
        (MESSAGE_TYPE_IMAGE, _("Image")),
        (MESSAGE_TYPE_VIDEO, _("Video")),
        (MESSAGE_TYPE_FILE, _("File")),
    ]

    message_type = models.CharField(
        _("message type"),
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default=MESSAGE_TYPE_TEXT,
    )
    # For non-text messages
    attachment = models.FileField(
        _("attachment"), upload_to="message_attachments/", blank=True, null=True
    )

    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        ordering = ["timestamp"]

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
