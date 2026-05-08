import json
import logging
import requests
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    queue='webhooks',
    name='apps.webhooks.tasks.send_webhook'
)
def send_webhook(self, delivery_id: str):
    from apps.webhooks.models import WebhookDelivery
    try:
        delivery = WebhookDelivery.objects.select_related('webhook').get(id=delivery_id)
    except WebhookDelivery.DoesNotExist:
        return

    webhook = delivery.webhook
    if not webhook.is_active:
        return

    payload_str = json.dumps(delivery.payload)
    signature = webhook.generate_signature(payload_str)

    headers = {
        'Content-Type': 'application/json',
        'X-EmailGuard-Signature': f'sha256={signature}',
        'X-EmailGuard-Event': delivery.event,
        'X-EmailGuard-Delivery': str(delivery.id),
        'User-Agent': 'EmailGuard-Webhooks/1.0',
    }

    delivery.attempt_count += 1

    try:
        response = requests.post(
            webhook.url,
            data=payload_str,
            headers=headers,
            timeout=30,
        )
        delivery.response_code = response.status_code
        delivery.response_body = response.text[:1000]

        if response.ok:
            delivery.status = 'success'
            delivery.delivered_at = timezone.now()
            webhook.total_deliveries += 1
        else:
            delivery.status = 'failed'
            webhook.failed_deliveries += 1
            raise Exception(f'HTTP {response.status_code}')

    except Exception as exc:
        delivery.status = 'failed' if delivery.attempt_count >= 5 else 'retrying'
        webhook.failed_deliveries += 1
        delivery.save()
        webhook.save(update_fields=['total_deliveries', 'failed_deliveries'])
        raise self.retry(exc=exc, countdown=60 * (2 ** delivery.attempt_count))

    delivery.save()
    webhook.last_triggered_at = timezone.now()
    webhook.save(update_fields=['total_deliveries', 'failed_deliveries', 'last_triggered_at'])


@shared_task(queue='webhooks', name='apps.webhooks.tasks.send_job_completion_webhooks')
def send_job_completion_webhooks(job_id: str):
    from apps.webhooks.models import Webhook, WebhookDelivery
    from apps.validation.models import BulkValidationJob

    try:
        job = BulkValidationJob.objects.get(id=job_id)
    except BulkValidationJob.DoesNotExist:
        return

    webhooks = Webhook.objects.filter(
        user=job.user,
        is_active=True,
        events__contains='bulk_job.completed'
    )

    payload = {
        'event': 'bulk_job.completed',
        'job_id': str(job.id),
        'filename': job.original_filename,
        'total_emails': job.total_emails,
        'valid_count': job.valid_count,
        'invalid_count': job.invalid_count,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
    }

    for webhook in webhooks:
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event='bulk_job.completed',
            payload=payload,
        )
        send_webhook.delay(str(delivery.id))
