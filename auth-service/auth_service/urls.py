from django.urls import path
from auth_service import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('health/', views.health, name='health'),
]
