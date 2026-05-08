from django.contrib import admin
from .models import Webhook, WebhookDelivery


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'url', 'is_active', 'total_deliveries', 'failed_deliveries']
    list_filter = ['is_active']
    search_fields = ['user__email', 'url']


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['webhook', 'event', 'status', 'response_code', 'attempt_count', 'created_at']
    list_filter = ['status', 'event']
    readonly_fields = ['id', 'created_at', 'delivered_at']
