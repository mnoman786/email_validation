from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'bulk', views.BulkJobViewSet, basename='bulk-jobs')

urlpatterns = [
    path('validate/', views.ValidateSingleEmailView.as_view(), name='validate-single'),
    path('history/', views.ValidationHistoryView.as_view(), name='validation-history'),
    path('stats/', views.ValidationStatsView.as_view(), name='validation-stats'),
    path('', include(router.urls)),
]
