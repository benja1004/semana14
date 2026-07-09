from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    App de dominio del servicio de autenticación.
    Sus modelos y migraciones viven aislados en 'authdb' (Database-per-Service).
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Cuentas de Autenticación'
