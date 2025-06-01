# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Explicitly create a DefaultRouter instance
router = DefaultRouter()

# Register the ConversationViewSet with the router
router.register(
    prefix="conversations", viewset=ConversationViewSet, basename="conversation"
)

# Register the MessageViewSet with the router
router.register(prefix="messages", viewset=MessageViewSet, basename="message")

urlpatterns = [
    # Include the router-generated URLs
    path("", include(router.urls)),
]
