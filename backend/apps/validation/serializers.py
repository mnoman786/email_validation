from rest_framework import serializers
from .models import ValidationResult, BulkValidationJob


class ValidationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationResult
        fields = [
            'id', 'email', 'status', 'score', 'is_valid',
            'local_part', 'domain', 'syntax_valid',
            'mx_found', 'mx_records', 'dns_valid',
            'smtp_check', 'smtp_connectable', 'smtp_response_code',
            'is_disposable', 'is_catch_all', 'is_role_account',
            'is_free_provider', 'is_spam_trap', 'is_greylisted', 'is_blacklisted',
            'domain_reputation', 'risk_level', 'suggested_action',
            'score_breakdown', 'processing_time_ms', 'validated_at',
        ]
        read_only_fields = fields


class ValidateSingleEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=512)
    check_smtp = serializers.BooleanField(default=True)


class BulkJobSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = BulkValidationJob
        fields = [
            'id', 'name', 'original_filename', 'status',
            'total_emails', 'processed_emails', 'progress_percentage',
            'valid_count', 'invalid_count', 'risky_count',
            'disposable_count', 'catch_all_count', 'spam_trap_count', 'unknown_count',
            'credits_used', 'created_at', 'started_at', 'completed_at',
            'duration_seconds', 'error_message',
        ]
        read_only_fields = fields


class BulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_file(self, value):
        from django.conf import settings
        max_size = getattr(settings, 'MAX_BULK_FILE_SIZE_MB', 50) * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File too large. Maximum size is {getattr(settings, "MAX_BULK_FILE_SIZE_MB", 50)}MB'
            )
        filename = value.name.lower()
        if not (filename.endswith('.csv') or filename.endswith('.txt')):
            raise serializers.ValidationError('Only CSV and TXT files are supported')
        return value


class ValidationStatsSerializer(serializers.Serializer):
    total_validations = serializers.IntegerField()
    valid_count = serializers.IntegerField()
    invalid_count = serializers.IntegerField()
    risky_count = serializers.IntegerField()
    disposable_count = serializers.IntegerField()
    catch_all_count = serializers.IntegerField()
    spam_trap_count = serializers.IntegerField()
    unknown_count = serializers.IntegerField()
    average_score = serializers.FloatField()
    valid_percentage = serializers.FloatField()
    total_bulk_jobs = serializers.IntegerField()
