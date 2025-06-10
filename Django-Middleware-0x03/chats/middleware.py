import logging
from datetime import datetime
from django.http import HttpResponseForbidden, JsonResponse
import time

# Configure logger
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("request_logs.txt")  # log to this file
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Allowed between 18 (6PM) and 21 (9PM), inclusive
        if current_hour < 18 or current_hour >= 21:
            return HttpResponseForbidden(
                "Access to the messaging app is restricted to 6PM - 9PM."
            )

        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_timestamps = {}  # Format: {ip: [timestamps]}

    def __call__(self, request):
        # Only track POST requests (e.g., chat messages)
        if request.method == "POST":
            ip = self.get_client_ip(request)
            now = time.time()

            # Clean old timestamps
            timestamps = self.ip_timestamps.get(ip, [])
            timestamps = [ts for ts in timestamps if now - ts < 60]  # last 60 seconds

            if len(timestamps) >= 5:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Max 5 messages per minute."},
                    status=429,
                )

            # Log current request
            timestamps.append(now)
            self.ip_timestamps[ip] = timestamps

        return self.get_response(request)

    def get_client_ip(self, request):
        """Handles possible proxy headers"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if user has a 'role' attribute
            user_role = getattr(request.user, "role", None)
            if user_role not in ["admin", "moderator"]:
                return HttpResponseForbidden("Access denied: insufficient permissions.")
        else:
            return HttpResponseForbidden("Access denied: login required.")

        return self.get_response(request)
