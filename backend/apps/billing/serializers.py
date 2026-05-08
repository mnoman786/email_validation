from rest_framework import serializers
from .models import Subscription, CreditPack, Payment, PLAN_CONFIGS


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_details = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'status', 'available_credits',
            'total_credits_purchased', 'total_credits_used',
            'trial_ends_at', 'current_period_start', 'current_period_end',
            'plan_details', 'created_at',
        ]
        read_only_fields = fields

    def get_plan_details(self, obj):
        return PLAN_CONFIGS.get(obj.plan, {})


class CreditPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPack
        fields = ['id', 'name', 'credits', 'price_usd', 'is_popular']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_type', 'status', 'amount_usd',
            'credits_added', 'description', 'created_at',
        ]
        read_only_fields = fields


class PurchaseCreditPackSerializer(serializers.Serializer):
    credit_pack_id = serializers.UUIDField()
    success_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)


class UpgradePlanSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=list(PLAN_CONFIGS.keys()))
    success_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)
