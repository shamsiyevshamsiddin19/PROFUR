"""Foydalanuvchi autentifikatsiyasi uchun URL marshrutlari."""

from accounts.views import CsrfTokenView, LoginView, LogoutView, MeView
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("csrf/", CsrfTokenView.as_view(), name="csrf"),
]
