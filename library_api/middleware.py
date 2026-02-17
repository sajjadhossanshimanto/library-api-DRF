from django.shortcuts import redirect
from django.contrib.auth.views import redirect_to_login
from urllib.parse import urlparse

class PublicSwaggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for Swagger or ReDoc
        path = request.path
        public_paths = ['/swagger/', '/redoc/']
        
        if any(path.startswith(p) for p in public_paths):
            request.is_public_swagger = True
        
        response = self.get_response(request)
        return response
