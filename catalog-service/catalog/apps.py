from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """
    App de dominio del servicio de catálogo.
    Sus modelos y migraciones viven aislados en 'catalogdb' (Database-per-Service).
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'
    verbose_name = 'Catálogo de Productos'
