"""Foydalanuvchi autentifikatsiyasi va profiliga oid API ko'rinishlari (views)."""

from accounts.serializers import LoginSerializer, UserSerializer
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):
    """Tizimga kirish (login) API'si. Sessiya cookie'sini o'rnatadi."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return Response(
                {
                    "message": "Tizimga muvaffaqiyatli kirildi.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Tizimdan chiqish (logout) API'si. Sessiyani yakunlaydi."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"message": "Tizimdan muvaffaqiyatli chiqildi."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Joriy tizimga kirgan foydalanuvchi profilini qaytaruvchi API."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CsrfTokenView(APIView):
    """Frontend (React) uchun CSRF tokenni taqdim etuvchi API."""

    permission_classes = [AllowAny]

    def get(self, request):
        token = get_token(request)
        return Response({"csrfToken": token}, status=status.HTTP_200_OK)
