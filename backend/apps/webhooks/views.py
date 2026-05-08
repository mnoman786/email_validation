import secrets
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Webhook, WebhookDelivery
from .serializers import WebhookSerializer, CreateWebhookSerializer, WebhookDeliverySerializer


@extend_schema(tags=['webhooks'])
class WebhookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateWebhookSerializer
        return WebhookSerializer

    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CreateWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self.get_queryset().count() >= 10:
            return Response(
                {'error': {'message': 'Maximum 10 webhooks allowed'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        webhook = Webhook.objects.create(
            user=request.user,
            name=serializer.validated_data['name'],
            url=serializer.validated_data['url'],
            events=serializer.validated_data['events'],
            secret=secrets.token_hex(32),
        )
        return Response({
            'success': True,
            'webhook': WebhookSerializer(webhook).data,
            'secret': webhook.secret,
            'note': 'Save this secret. It is used to verify webhook signatures.',
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='test')
    def test(self, request, pk=None):
        webhook = self.get_object()
        from .tasks import send_webhook
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event='test',
            payload={'event': 'test', 'message': 'This is a test webhook delivery'},
        )
        send_webhook.delay(str(delivery.id))
        return Response({'success': True, 'message': 'Test webhook queued', 'delivery_id': str(delivery.id)})

    @action(detail=True, methods=['get'], url_path='deliveries')
    def deliveries(self, request, pk=None):
        webhook = self.get_object()
        deliveries = WebhookDelivery.objects.filter(webhook=webhook)[:50]
        return Response(WebhookDeliverySerializer(deliveries, many=True).data)
