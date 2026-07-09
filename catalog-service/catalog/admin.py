from django.contrib import admin

from catalog.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock', 'is_available', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_available',)
