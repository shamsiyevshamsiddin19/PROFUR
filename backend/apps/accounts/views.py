"""Foydalanuvchi autentifikatsiyasi, rollar va profiliga oid API ko'rinishlari (views)."""

from accounts.models import Role
from accounts.permissions import IsAdminRole
from accounts.serializers import LoginSerializer, RoleSerializer, UserSerializer
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(APIView):
    """Frontend (React) uchun CSRF tokenni taqdim etuvchi API."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        token = get_token(request)
        return Response({"csrfToken": token}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    """
    Tizimga kirish (login) API'si.

    CSRF himoyasi yoqilgan: so'rovda CSRF token bo'lishi shart.
    Muvaffaqiyatli kirilganda sessiya cookie'si o'rnatiladi.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return Response(
                {
                    "message": _("Tizimga muvaffaqiyatli kirildi."),
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
            {"message": _("Tizimdan muvaffaqiyatli chiqildi.")},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Joriy tizimga kirgan foydalanuvchi profilini qaytaruvchi API."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoleListCreateView(generics.ListCreateAPIView):
    """
    Rollar ro'yxatini ko'rish va yangi rol yaratish API'si (OQ-037).

    Rollar ro'yxatini tizimga kirgan barcha xodimlar ko'rishi mumkin.
    Yangi rol yaratish faqat administratorga ruxsat etiladi.
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [IsAuthenticated()]


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Rolni ko'rish, tahrirlash va o'chirish API'si (faqat Admin)."""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminRole]
