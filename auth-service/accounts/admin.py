from django.contrib import admin

from accounts.models import UserAccount


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_active',)
