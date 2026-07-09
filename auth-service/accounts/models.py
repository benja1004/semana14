from django.db import models


class UserAccount(models.Model):
    """
    Cuenta de usuario del dominio de autenticación.

    Persistida exclusivamente en 'authdb'. El servicio de catálogo NO tiene
    acceso a esta tabla: cualquier dato de usuario que necesite lo obtiene
    vía el token JWT o mediante llamadas HTTP inter-servicio (Database-per-Service).
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, blank=True)
    # Hash de contraseña (nunca se almacena en texto plano).
    password_hash = models.CharField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_user_account'
        ordering = ['username']
        verbose_name = 'Cuenta de Usuario'
        verbose_name_plural = 'Cuentas de Usuario'

    def __str__(self):
        return self.username
