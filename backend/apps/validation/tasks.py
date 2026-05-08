import logging
from celery import shared_task, chord, group
from django.utils import timezone
from django.db import transaction
from django.conf import settings

logger = logging.getLogger(__name__)

BATCH_SIZE = getattr(settings, 'VALIDATION_BATCH_SIZE', 100)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue='validation',
    name='apps.validation.tasks.validate_single_email'
)
def validate_single_email(self, email: str, user_id: str = None, job_id: str = None):
    """Validate a single email asynchronously."""
    try:
        from apps.validation.engine import EmailValidator
        validator = EmailValidator(check_smtp=True)
        validation_data = validator.validate(email)

        from apps.validation.models import ValidationResult, BulkValidationJob
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        bulk_job = None
        if job_id:
            try:
                bulk_job = BulkValidationJob.objects.get(id=job_id)
            except BulkValidationJob.DoesNotExist:
                pass

        result = ValidationResult.objects.create(
            user=user,
            bulk_job=bulk_job,
            email=validation_data.email,
            original_email=validation_data.original_email or email,
            status=validation_data.status,
            score=validation_data.score,
            is_valid=validation_data.is_valid,
            local_part=validation_data.local_part,
            domain=validation_data.domain,
            syntax_valid=validation_data.syntax_valid,
            mx_found=validation_data.mx_found,
            mx_records=validation_data.mx_records,
            dns_valid=validation_data.dns_valid,
            smtp_check=validation_data.smtp_check,
            smtp_connectable=validation_data.smtp_connectable,
            smtp_response_code=validation_data.smtp_response_code,
            is_disposable=validation_data.is_disposable,
            is_catch_all=validation_data.is_catch_all,
            is_role_account=validation_data.is_role_account,
            is_free_provider=validation_data.is_free_provider,
            is_spam_trap=validation_data.is_spam_trap,
            is_greylisted=validation_data.is_greylisted,
            domain_reputation=validation_data.domain_reputation,
            risk_level=validation_data.risk_level,
            suggested_action=validation_data.suggested_action,
            score_breakdown=validation_data.score_breakdown,
            processing_time_ms=validation_data.processing_time_ms,
            api_source='async',
        )
        return str(result.id)

    except Exception as exc:
        logger.error(f'validate_single_email error for {email}: {exc}')
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=2,
    queue='bulk',
    name='apps.validation.tasks.validate_email_batch'
)
def validate_email_batch(self, emails: list, job_id: str, user_id: str):
    """Validate a batch of emails and update job progress."""
    from apps.validation.models import BulkValidationJob, ValidationResult
    from apps.validation.engine import EmailValidator
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        job = BulkValidationJob.objects.get(id=job_id)
        user = User.objects.get(id=user_id)
    except Exception as e:
        logger.error(f'Failed to load job/user: {e}')
        return

    validator = EmailValidator(check_smtp=True)
    results_to_create = []
    status_counts = {
        'valid': 0, 'invalid': 0, 'risky': 0,
        'disposable': 0, 'catch_all': 0, 'spam_trap': 0, 'unknown': 0,
    }

    for email in emails:
        try:
            vd = validator.validate(email)
            results_to_create.append(ValidationResult(
                user=user,
                bulk_job=job,
                email=vd.email,
                original_email=vd.original_email or email,
                status=vd.status,
                score=vd.score,
                is_valid=vd.is_valid,
                local_part=vd.local_part,
                domain=vd.domain,
                syntax_valid=vd.syntax_valid,
                mx_found=vd.mx_found,
                mx_records=vd.mx_records,
                dns_valid=vd.dns_valid,
                smtp_check=vd.smtp_check,
                smtp_connectable=vd.smtp_connectable,
                smtp_response_code=vd.smtp_response_code,
                is_disposable=vd.is_disposable,
                is_catch_all=vd.is_catch_all,
                is_role_account=vd.is_role_account,
                is_free_provider=vd.is_free_provider,
                is_spam_trap=vd.is_spam_trap,
                is_greylisted=vd.is_greylisted,
                domain_reputation=vd.domain_reputation,
                risk_level=vd.risk_level,
                suggested_action=vd.suggested_action,
                score_breakdown=vd.score_breakdown,
                processing_time_ms=vd.processing_time_ms,
                api_source='bulk',
            ))
            status_counts[vd.status] = status_counts.get(vd.status, 0) + 1
        except Exception as e:
            logger.warning(f'Failed to validate {email}: {e}')
            status_counts['unknown'] = status_counts.get('unknown', 0) + 1

    # Bulk create
    from django.db.models import F
    with transaction.atomic():
        ValidationResult.objects.bulk_create(results_to_create, batch_size=500)
        BulkValidationJob.objects.filter(id=job_id).update(
            processed_emails=F('processed_emails') + len(emails),
            valid_count=F('valid_count') + status_counts.get('valid', 0),
            invalid_count=F('invalid_count') + status_counts.get('invalid', 0),
            risky_count=F('risky_count') + status_counts.get('risky', 0),
            disposable_count=F('disposable_count') + status_counts.get('disposable', 0),
            catch_all_count=F('catch_all_count') + status_counts.get('catch_all', 0),
            spam_trap_count=F('spam_trap_count') + status_counts.get('spam_trap', 0),
            unknown_count=F('unknown_count') + status_counts.get('unknown', 0),
        )

    return len(results_to_create)


@shared_task(
    bind=True,
    max_retries=1,
    queue='bulk',
    name='apps.validation.tasks.process_bulk_validation'
)
def process_bulk_validation(self, job_id: str):
    """Orchestrate bulk email validation by splitting into batches."""
    from apps.validation.models import BulkValidationJob

    try:
        job = BulkValidationJob.objects.get(id=job_id)
    except BulkValidationJob.DoesNotExist:
        logger.error(f'Job {job_id} not found')
        return

    job.status = 'processing'
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at'])

    try:
        # Read emails from file
        with open(job.file_path, 'r', encoding='utf-8') as f:
            emails = [line.strip() for line in f if line.strip()]

        if not emails:
            job.status = 'failed'
            job.error_message = 'No emails found in file'
            job.save(update_fields=['status', 'error_message'])
            return

        job.total_emails = len(emails)
        job.save(update_fields=['total_emails'])

        # Split into batches and dispatch
        user_id = str(job.user_id)
        batches = [emails[i:i + BATCH_SIZE] for i in range(0, len(emails), BATCH_SIZE)]

        batch_tasks = group(
            validate_email_batch.s(batch, job_id, user_id)
            for batch in batches
        )
        result = batch_tasks.apply_async()

        # Wait for all batches to complete
        result.get(timeout=3600, propagate=False)

        # Mark job complete
        job.refresh_from_db()
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.credits_used = job.total_emails
        job.save(update_fields=['status', 'completed_at', 'credits_used'])

        # Fire webhook
        from apps.webhooks.tasks import send_job_completion_webhooks
        send_job_completion_webhooks.delay(job_id)

    except Exception as exc:
        logger.error(f'Bulk validation failed for job {job_id}: {exc}', exc_info=True)
        job.status = 'failed'
        job.error_message = str(exc)
        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'completed_at'])
        raise self.retry(exc=exc)
