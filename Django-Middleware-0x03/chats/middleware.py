import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('request_logs.txt')  # log to this file
formatter = logging.Formatter('%(message)s')
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
