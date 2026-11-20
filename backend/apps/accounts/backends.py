"""Faqat tasdiqlangan foydalanuvchilarga kirish ruxsati beruvchi backend."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class ApprovedUserBackend(ModelBackend):
    """Only allow login for approved users."""

    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and user.is_approved
