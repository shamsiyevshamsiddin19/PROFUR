"""Xarajatlar API'si uchun ruxsat tekshiruvi.

API foydalanuvchi rolining nomini emas, Django ruxsat kodini tekshiradi
(OQ-037: rollarni admin erkin yaratadi). Qaysi rolga qaysi ruxsat berilishi
``accounts`` ilovasida belgilanadi (PCRM-32).

Kelishilmagan nuqta: PCRM-49 API shartnomasi Django ruxsatlarini taklif qiladi,
PCRM-32 tarmog'ida esa rol ichida o'z ruxsat kodlari (``has_permission_code``)
bor. Tekshiruv faqat shu faylda, shuning uchun kelishuvdan keyin bitta joy
o'zgaradi.
"""

from rest_framework.permissions import BasePermission


class HasActionPermission(BasePermission):
    """View'dagi ``required_permissions`` lug'ati bo'yicha ruxsatni tekshiradi.

    Lug'at kaliti — DRF amali (``list``, ``create`` ...), qiymati — kerakli
    Django ruxsat kodlari. Lug'atda yo'q amal rad etiladi, shunda yangi amal
    qo'shilganda ruxsatni unutib qoldirish xavfi yo'q.

    Manzilda umuman yo'q metod (masalan, ``DELETE``) uchun ``view.action``
    bo'sh bo'ladi. Uni o'tkazib yuboramiz, shunda DRF to'g'ri 405 javobini
    qaytaradi va hech qanday amal bajarilmaydi.
    """

    def has_permission(self, request, view) -> bool:
        """Foydalanuvchi kirganini va amal uchun barcha ruxsatlari borligini tekshiradi."""
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if view.action is None:
            return True
        required = getattr(view, "required_permissions", {}).get(view.action)
        if required is None:
            return False
        return user.has_perms(required)
