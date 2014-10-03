import django

__all__ = ['User', 'get_user_model']


# This small file just keeps the app compatible with Django versions 1.5+ and
# < 1.5. There are some "unused" imports like `get_user_model` or `User` but
# they are ther to get imported like `from .compat import get_user_model`

if django.VERSION >= (1, 5):
    from django.conf import settings
    from django.contrib.auth import get_user_model
    User = settings.AUTH_USER_MODEL if hasattr(settings, 'AUTH_USER_MODEL') else 'auth.User'

else:
    from django.contrib.auth.models import User

    def get_user_model():
        return User
