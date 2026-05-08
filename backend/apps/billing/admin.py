from django.contrib import admin
from .models import Subscription, CreditPack, Payment


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'available_credits', 'total_credits_used', 'created_at']
    list_filter = ['plan', 'status']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_credits_purchased', 'total_credits_used']


@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'credits', 'price_usd', 'is_active', 'is_popular']
    list_filter = ['is_active', 'is_popular']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'status', 'amount_usd', 'credits_added', 'created_at']
    list_filter = ['payment_type', 'status']
    search_fields = ['user__email', 'stripe_payment_intent_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
