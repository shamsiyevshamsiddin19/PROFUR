"""Faqat tasdiqlangan foydalanuvchilarga kirish ruxsati beruvchi backend."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class ApprovedUserBackend(ModelBackend):
    """Only allow login for approved users."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(
            request, username=username, password=password, **kwargs
        )
        if user and not user.is_approved:
            return None
        return user
