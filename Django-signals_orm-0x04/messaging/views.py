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
