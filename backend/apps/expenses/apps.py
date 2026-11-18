from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExpensesConfig(AppConfig):
    """Qo'shimcha xarajatlar ilovasi: xarajat turlari va xarajat yozuvlari."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.expenses"
    label = "expenses"
    verbose_name = _("Qo'shimcha xarajatlar")
