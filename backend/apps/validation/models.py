import uuid
from django.db import models
from django.conf import settings


class ValidationResult(models.Model):
    STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('risky', 'Risky'),
        ('disposable', 'Disposable'),
        ('spam_trap', 'Spam Trap'),
        ('catch_all', 'Catch All'),
        ('unknown', 'Unknown'),
    ]

    RISK_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    REPUTATION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('unknown', 'Unknown'),
    ]

    ACTION_CHOICES = [
        ('safe_to_send', 'Safe to Send'),
        ('send_with_caution', 'Send with Caution'),
        ('do_not_send', 'Do Not Send'),
        ('unknown', 'Unknown'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='validations'
    )
    bulk_job = models.ForeignKey(
        'BulkValidationJob',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results'
    )

    # Input
    email = models.EmailField(db_index=True)
    original_email = models.CharField(max_length=512)

    # Core results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    score = models.IntegerField(default=0)
    is_valid = models.BooleanField(default=False)

    # Email structure
    local_part = models.CharField(max_length=255, blank=True)
    domain = models.CharField(max_length=255, blank=True, db_index=True)
    syntax_valid = models.BooleanField(default=False)

    # DNS / MX
    mx_found = models.BooleanField(default=False)
    mx_records = models.JSONField(default=list)
    dns_valid = models.BooleanField(default=False)

    # SMTP
    smtp_check = models.BooleanField(default=False)
    smtp_connectable = models.BooleanField(default=False)
    smtp_response_code = models.IntegerField(null=True, blank=True)

    # Email characteristics
    is_disposable = models.BooleanField(default=False)
    is_catch_all = models.BooleanField(default=False)
    is_role_account = models.BooleanField(default=False)
    is_free_provider = models.BooleanField(default=False)
    is_spam_trap = models.BooleanField(default=False)
    is_greylisted = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)

    # Reputation
    domain_reputation = models.CharField(max_length=20, choices=REPUTATION_CHOICES, default='unknown')
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='low')
    suggested_action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='unknown')

    # Score breakdown
    score_breakdown = models.JSONField(default=dict)

    # Processing
    processing_time_ms = models.IntegerField(default=0)
    validated_at = models.DateTimeField(auto_now_add=True)
    api_source = models.CharField(max_length=50, default='web')

    class Meta:
        db_table = 'validation_results'
        ordering = ['-validated_at']
        indexes = [
            models.Index(fields=['user', 'validated_at']),
            models.Index(fields=['email']),
            models.Index(fields=['domain']),
            models.Index(fields=['status']),
            models.Index(fields=['bulk_job']),
        ]

    def __str__(self):
        return f'{self.email} - {self.status} ({self.score})'

    def to_api_response(self):
        return {
            'email': self.email,
            'valid': self.is_valid,
            'score': self.score,
            'status': self.status,
            'is_disposable': self.is_disposable,
            'is_catch_all': self.is_catch_all,
            'is_role_account': self.is_role_account,
            'is_free_provider': self.is_free_provider,
            'is_spam_trap': self.is_spam_trap,
            'is_greylisted': self.is_greylisted,
            'is_blacklisted': self.is_blacklisted,
            'smtp_check': self.smtp_check,
            'smtp_connectable': self.smtp_connectable,
            'smtp_response_code': self.smtp_response_code,
            'mx_found': self.mx_found,
            'mx_records': self.mx_records or [],
            'dns_valid': self.dns_valid,
            'local_part': self.local_part,
            'domain': self.domain,
            'syntax_valid': self.syntax_valid,
            'domain_reputation': self.domain_reputation,
            'risk_level': self.risk_level,
            'suggested_action': self.suggested_action,
            'score_breakdown': self.score_breakdown,
            'processing_time_ms': self.processing_time_ms,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
        }


class BulkValidationJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bulk_jobs'
    )
    name = models.CharField(max_length=255, blank=True)
    original_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Progress
    total_emails = models.IntegerField(default=0)
    processed_emails = models.IntegerField(default=0)
    valid_count = models.IntegerField(default=0)
    invalid_count = models.IntegerField(default=0)
    risky_count = models.IntegerField(default=0)
    disposable_count = models.IntegerField(default=0)
    catch_all_count = models.IntegerField(default=0)
    spam_trap_count = models.IntegerField(default=0)
    unknown_count = models.IntegerField(default=0)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Results
    result_file_path = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)

    # Credits
    credits_used = models.IntegerField(default=0)

    class Meta:
        db_table = 'bulk_validation_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.original_filename} - {self.status}'

    @property
    def progress_percentage(self):
        if self.total_emails == 0:
            return 0
        return round((self.processed_emails / self.total_emails) * 100, 1)

    @property
    def duration_seconds(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class DisposableDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    added_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100, default='manual')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'disposable_domains'

    def __str__(self):
        return self.domain


class SpamTrapDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    email_pattern = models.CharField(max_length=255, blank=True)
    confidence = models.FloatField(default=1.0)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'spam_trap_domains'


class DomainCache(models.Model):
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    mx_found = models.BooleanField(default=False)
    mx_records = models.JSONField(default=list)
    is_catch_all = models.BooleanField(default=False)
    is_disposable = models.BooleanField(default=False)
    reputation = models.CharField(max_length=20, default='unknown')
    cached_at = models.DateTimeField(auto_now=True)
    ttl_hours = models.IntegerField(default=24)

    class Meta:
        db_table = 'domain_cache'
        indexes = [models.Index(fields=['domain', 'cached_at'])]
