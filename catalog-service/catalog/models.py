from django.db import models


class Product(models.Model):
    """
    Producto del dominio de catálogo.

    Persistido exclusivamente en 'catalogdb'. Este servicio no comparte base de
    datos con auth-service: la identidad del usuario que consulta el catálogo se
    resuelve a partir del token JWT, no de una tabla compartida (Database-per-Service).
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalog_product'
        ordering = ['name']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.name
