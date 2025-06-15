from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User


@login_required
def delete_user(request):
    if request.method == "POST":
        user = request.user
        logout(request)  # Log out before deleting to prevent issues
        user.delete()  # This will trigger our post_delete signal
        messages.success(request, "Your account has been successfully deleted.")
        return redirect("home")
    return render(request, "accounts/confirm_delete.html")


@login_required
def conversation_thread(request, message_id):
    """View a complete conversation thread with optimized queries"""
    base_message = get_object_or_404(
        Message.objects.select_related("sender", "receiver").prefetch_related(
            Prefetch(
                "replies",
                queryset=Message.objects.select_related("sender", "receiver").order_by(
                    "timestamp"
                ),
            )
        ),
        id=message_id,
        receiver=request.user,  # Only allow viewing messages sent to current user
    )

    # Get the entire thread
    thread_messages = base_message.get_thread()

    return render(
        request,
        "messaging/thread.html",
        {
            "base_message": base_message,
            "thread_messages": sorted(thread_messages, key=lambda x: x.timestamp),
        },
    )


@login_required
def inbox(request):
    """Show all conversations with their latest messages"""
    # Get all threads where the user is involved (either sender or receiver)
    # and prefetch the latest message in each thread
    threads = (
        Message.objects.filter(
            models.Q(sender=request.user) | models.Q(receiver=request.user)
        )
        .filter(parent_message__isnull=True)  # Only show root messages (not replies)
        .select_related("sender", "receiver")
        .prefetch_related(
            Prefetch(
                "replies",
                queryset=Message.objects.select_related("sender", "receiver").order_by(
                    "-timestamp"
                ),
            )
        )
        .order_by("-timestamp")
    )

    return render(request, "messaging/inbox.html", {"threads": threads})
