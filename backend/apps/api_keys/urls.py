from django.urls import path
from . import views

urlpatterns = [
    path('', views.APIKeyListCreateView.as_view(), name='api-keys'),
    path('<uuid:pk>/', views.APIKeyDetailView.as_view(), name='api-key-detail'),
]
