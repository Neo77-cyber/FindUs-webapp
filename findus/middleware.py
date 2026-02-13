# middleware.py
from django.db import connection

class SimpleDBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Just one line - check connection
        connection.ensure_connection()
        return self.get_response(request)