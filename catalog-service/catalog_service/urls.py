from django.urls import path
from catalog_service import views

urlpatterns = [
    path('catalog/', views.catalog_list, name='catalog_list'),
    path('health/', views.health, name='health'),
]
