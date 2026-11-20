"""Foydalanuvchi autentifikatsiyasi va rollar uchun URL marshrutlari."""

from accounts.views import (
    ApproveUserView,
    CsrfTokenView,
    LoginView,
    LogoutView,
    MeView,
    PendingUsersView,
    RegisterView,
    RejectUserView,
    RoleDetailView,
    RoleListCreateView,
    SignupRolesView,
    UserDeactivateView,
    UserDetailView,
    UserListCreateView,
    UserResetPasswordView,
)
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path("signup-roles/", SignupRolesView.as_view(), name="signup-roles"),
    path("register/", RegisterView.as_view(), name="register"),
    path("pending/", PendingUsersView.as_view(), name="pending-users"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("csrf/", CsrfTokenView.as_view(), name="csrf"),
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path(
        "users/<int:pk>/deactivate/",
        UserDeactivateView.as_view(),
        name="user-deactivate",
    ),
    path(
        "users/<int:pk>/reset-password/",
        UserResetPasswordView.as_view(),
        name="user-reset-password",
    ),
    path(
        "users/<int:pk>/approve/",
        ApproveUserView.as_view(),
        name="approve-user",
    ),
    path(
        "users/<int:pk>/reject/",
        RejectUserView.as_view(),
        name="reject-user",
    ),
]
