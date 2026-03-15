from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FinancesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finances'
    verbose_name = _('Finances')

    def ready(self):
        import apps.finances.signals
