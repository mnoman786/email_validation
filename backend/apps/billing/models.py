import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


PLAN_CONFIGS = {
    'free': {'credits': 100, 'price': 0, 'name': 'Free', 'features': ['100 verifications/month']},
    'starter': {'credits': 5000, 'price': 19, 'name': 'Starter', 'features': ['5,000 verifications/month', 'API access', 'CSV export']},
    'growth': {'credits': 25000, 'price': 49, 'name': 'Growth', 'features': ['25,000 verifications/month', 'API access', 'CSV export', 'Webhooks']},
    'pro': {'credits': 100000, 'price': 99, 'name': 'Pro', 'features': ['100,000 verifications/month', 'API access', 'Priority support', 'Webhooks', 'Advanced analytics']},
    'enterprise': {'credits': 1000000, 'price': 299, 'name': 'Enterprise', 'features': ['1,000,000 verifications/month', 'Dedicated support', 'SLA', 'Custom integrations']},
    'payg': {'credits': 0, 'price': 0, 'name': 'Pay As You Go', 'features': ['Flexible usage', 'No monthly commitment']},
}


class Subscription(models.Model):
    PLAN_CHOICES = [(k, v['name']) for k, v in PLAN_CONFIGS.items()]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('trialing', 'Trialing'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Credits
    available_credits = models.BigIntegerField(default=0)
    total_credits_purchased = models.BigIntegerField(default=0)
    total_credits_used = models.BigIntegerField(default=0)

    # Stripe
    stripe_customer_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, db_index=True)

    # Dates
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'

    def __str__(self):
        return f'{self.user.email} - {self.plan}'

    def use_credits(self, amount: int):
        if self.available_credits >= amount:
            self.available_credits -= amount
            self.total_credits_used += amount
            self.save(update_fields=['available_credits', 'total_credits_used'])
            return True
        return False

    def add_credits(self, amount: int):
        self.available_credits += amount
        self.total_credits_purchased += amount
        self.save(update_fields=['available_credits', 'total_credits_purchased'])

    @property
    def is_active(self):
        return self.status in ('active', 'trialing')


class CreditPack(models.Model):
    """Pre-defined credit packages for purchase."""
    name = models.CharField(max_length=100)
    credits = models.IntegerField()
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)

    class Meta:
        db_table = 'credit_packs'
        ordering = ['credits']

    def __str__(self):
        return f'{self.name} - {self.credits} credits'


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('credit_pack', 'Credit Pack'),
        ('one_time', 'One Time'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    credits_added = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)

    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_invoice_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'status'])]
