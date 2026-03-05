class PublicSwaggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that should be publicly accessible
        self.public_paths = ['/swagger/', '/redoc/', '/swagger']

    def __call__(self, request):
        path = request.path
        
        # Mark swagger paths as public
        if any(path.startswith(p) for p in self.public_paths) or path == '/swagger':
            request.is_public_swagger = True
            # Ensure no authentication is required for these endpoints
            request.META['HTTP_AUTHORIZATION'] = ''
        
        response = self.get_response(request)
        return response
