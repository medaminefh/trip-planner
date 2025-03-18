import os

class XFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Allow framing from localhost:3000 during development
        if os.getenv('DEBUG', 'False') == 'True' and request.get_host() == 'localhost:8000':
            response['X-Frame-Options'] = 'ALLOW-FROM http://localhost:3000'
        return response