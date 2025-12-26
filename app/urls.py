from django.urls import path
from . import views

urlpatterns = [
    path('api/activate_license/', views.start_activation, name='activate-license'),
    path('api/health/', views.health_check, name='health-check'),
]
