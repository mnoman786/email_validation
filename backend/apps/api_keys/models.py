import uuid
import secrets
import hashlib
from django.db import models
from django.conf import settings
from django.utils import timezone


def generate_api_key():
    return f'eg_{secrets.token_urlsafe(32)}'


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


class APIKey(models.Model):
    PERMISSION_CHOICES = [
        ('read', 'Read Only'),
        ('validate', 'Validate Emails'),
        ('bulk', 'Bulk Operations'),
        ('full', 'Full Access'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    name = models.CharField(max_length=100)
    key_hash = models.CharField(max_length=64, unique=True, db_index=True)
    key_prefix = models.CharField(max_length=12)
    permissions = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='validate')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Rate limiting
    rate_limit_per_hour = models.IntegerField(default=1000)
    total_requests = models.BigIntegerField(default=0)

    # IP whitelist
    allowed_ips = models.JSONField(default=list)

    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['key_hash', 'is_active'])]

    def __str__(self):
        return f'{self.user.email} - {self.name}'

    @classmethod
    def create_key(cls, user, name: str, permissions: str = 'validate', **kwargs) -> tuple:
        """Create a new API key. Returns (APIKey instance, raw_key)."""
        raw_key = generate_api_key()
        key_hash = hash_key(raw_key)
        key_prefix = raw_key[:12]

        api_key = cls.objects.create(
            user=user,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=permissions,
            **kwargs,
        )
        return api_key, raw_key

    @classmethod
    def authenticate(cls, raw_key: str):
        """Authenticate and return APIKey instance or None."""
        key_hash = hash_key(raw_key)
        try:
            api_key = cls.objects.select_related('user').get(
                key_hash=key_hash,
                is_active=True,
            )
            if api_key.expires_at and api_key.expires_at < timezone.now():
                return None
            return api_key
        except cls.DoesNotExist:
            return None

    def record_usage(self):
        self.last_used_at = timezone.now()
        self.total_requests += 1
        self.save(update_fields=['last_used_at', 'total_requests'])
