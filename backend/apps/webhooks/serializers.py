from rest_framework import serializers
from .models import Webhook, WebhookDelivery


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'events', 'is_active',
            'created_at', 'last_triggered_at', 'total_deliveries', 'failed_deliveries',
        ]
        read_only_fields = ['id', 'created_at', 'last_triggered_at', 'total_deliveries', 'failed_deliveries']


class CreateWebhookSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    url = serializers.URLField()
    events = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'bulk_job.completed', 'bulk_job.failed',
            'validation.completed', 'credits.low', 'subscription.cancelled',
        ]),
        min_length=1,
    )


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = ['id', 'event', 'status', 'response_code', 'attempt_count', 'created_at', 'delivered_at']
