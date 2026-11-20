from accounts.models import Role, User
from accounts.permissions import IsAdminRole
from accounts.serializers import (
    LoginSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    RoleSerializer,
    UserAdminCreateSerializer,
    UserAdminUpdateSerializer,
    UserSerializer,
)
from django.contrib.auth import login, logout
from django.db.models import Q
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
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

    def perform_destroy(self, instance):
        if instance.is_system or instance.code == "ADMIN" or instance.users.exists():
            raise ValidationError(
                _("Tizimli yoki foydalanuvchiga biriktirilgan rol o'chirilmaydi.")
            )
        instance.delete()


class UserListCreateView(generics.ListCreateAPIView):
    """
    Admin tomonidan foydalanuvchilar ro'yxatini ko'rish va yangi yaratish (OQ-040).
    Faqat administrator uchun ochiq.
    """

    permission_classes = [IsAdminRole]
    queryset = User.objects.all().prefetch_related("roles")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserAdminCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        if search := params.get("search", "").strip():
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        if is_active_param := params.get("is_active"):
            if is_active_param.lower() in ("true", "1"):
                queryset = queryset.filter(is_active=True)
            elif is_active_param.lower() in ("false", "0"):
                queryset = queryset.filter(is_active=False)
        return queryset


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Foydalanuvchi ma'lumotlarini ko'rish va yangilash (OQ-040).
    OQ-040 bo'yicha akkaunt bazadan o'chirilmaydi (DELETE 405 Method Not Allowed).
    """

    permission_classes = [IsAdminRole]
    queryset = User.objects.all().prefetch_related("roles")
    serializer_class = UserAdminUpdateSerializer
    http_method_names = ["get", "patch", "put", "head", "options"]


class UserDeactivateView(APIView):
    """
    Foydalanuvchi hisobini faolsizlantirish API'si (OQ-040).
    Akkaunt o'chirilmaydi, faolsizlantiriladi va ish tarixi saqlanadi.
    """

    permission_classes = [IsAdminRole]

    def post(self, request, pk: int):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": _("Foydalanuvchi topilmadi.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if target_user.pk == request.user.pk:
            raise ValidationError(_("O'z hisobingizni faolsizlantira olmaysiz."))
        target_user.is_active = False
        target_user.save(update_fields=["is_active"])
        return Response(
            {
                "message": _("Foydalanuvchi muvaffaqiyatli faolsizlantirildi."),
                "user": UserSerializer(target_user).data,
            },
            status=status.HTTP_200_OK,
        )


class UserResetPasswordView(APIView):
    """
    Foydalanuvchi parolini tiklash API'si (OQ-040).
    Faqat administrator amalga oshira oladi.
    """

    permission_classes = [IsAdminRole]

    def post(self, request, pk: int):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": _("Foydalanuvchi topilmadi.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PasswordResetSerializer(
            data=request.data, context={"user": target_user}
        )
        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]
            target_user.set_password(new_password)
            target_user.save(update_fields=["password"])
            return Response(
                {"message": _("Parol muvaffaqiyatli yangilandi.")},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """Ishchi o'z-o'zini ro'yxatdan o'tkazish API'si. Admin tasdiqini kutadi."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "registration"

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(
            {"detail": "Registration submitted. Waiting for admin approval."},
            status=status.HTTP_201_CREATED,
        )


class PendingUsersView(APIView):
    """Tasdiqlash kutayotgan foydalanuvchilar ro'yxati."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        pending = User.objects.filter(is_approved=False, is_active=True)
        data = [
            {
                "id": u.id,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "phone": u.phone,
                "date_joined": u.date_joined,
            }
            for u in pending
        ]
        return Response(data)


class ApproveUserView(APIView):
    """Kutayotgan foydalanuvchini tasdiqlash."""

    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": _("Foydalanuvchi topilmadi.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        role_ids = request.data.get("role_ids", [])
        if role_ids:
            roles = Role.objects.filter(id__in=role_ids)
            user.roles.set(roles)

        user.is_approved = True
        user.save(update_fields=["is_approved"])
        return Response({"detail": _("Foydalanuvchi tasdiqlandi.")})


class RejectUserView(APIView):
    """Kutayotgan foydalanuvchini rad etish (o'chirish)."""

    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_approved=False)
        except User.DoesNotExist:
            return Response(
                {"detail": _("Kutayotgan foydalanuvchi topilmadi.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.delete()
        return Response({"detail": _("Foydalanuvchi rad etildi va o'chirildi.")})
