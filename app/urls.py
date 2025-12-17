from django.urls import path
from . import views

urlpatterns = [
    path('api/license-activation', views.start_activation, name='license-activation'),
    path('api/health/', views.health_check, name='health-check'),
]
