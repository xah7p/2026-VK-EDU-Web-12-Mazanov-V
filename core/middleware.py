from django.contrib.auth import get_user_model, logout

User = get_user_model()


class InvalidateDeletedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        u = request.user
        if u.is_authenticated and not User.objects.filter(pk=u.pk).exists():
            logout(request)
        return self.get_response(request)
