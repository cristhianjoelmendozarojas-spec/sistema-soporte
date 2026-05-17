from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = request.user.profile
            allowed_paths = [
                reverse('users:cambiar_password'),
                reverse('users:logout'),
                reverse('users:login'),
                '/admin/',
            ]
            if profile.cambiar_password and request.path not in allowed_paths and not request.path.startswith('/static/'):
                return redirect('users:cambiar_password')
        return self.get_response(request)
