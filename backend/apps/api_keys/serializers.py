from rest_framework import serializers
from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_prefix', 'permissions',
            'is_active', 'created_at', 'last_used_at', 'expires_at',
            'rate_limit_per_hour', 'total_requests', 'allowed_ips',
        ]
        read_only_fields = ['id', 'key_prefix', 'created_at', 'last_used_at', 'total_requests']


class CreateAPIKeySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    permissions = serializers.ChoiceField(
        choices=['read', 'validate', 'bulk', 'full'],
        default='validate'
    )
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    allowed_ips = serializers.ListField(
        child=serializers.IPAddressField(),
        required=False,
        allow_empty=True,
    )
    rate_limit_per_hour = serializers.IntegerField(default=1000, min_value=1, max_value=100000)


class APIKeyCreatedSerializer(serializers.Serializer):
    """Response after creating an API key - includes the raw key (shown once)."""
    id = serializers.UUIDField()
    name = serializers.CharField()
    key = serializers.CharField(help_text='Raw API key - save this, it will not be shown again')
    key_prefix = serializers.CharField()
    permissions = serializers.CharField()
    created_at = serializers.DateTimeField()
