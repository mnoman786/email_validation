from django.contrib import admin
from django.utils.html import format_html
from .models import ValidationResult, BulkValidationJob, DisposableDomain, SpamTrapDomain, DomainCache


@admin.register(ValidationResult)
class ValidationResultAdmin(admin.ModelAdmin):
    list_display = ['email', 'status_badge', 'score', 'domain', 'is_disposable', 'is_catch_all', 'validated_at']
    list_filter = ['status', 'is_disposable', 'is_catch_all', 'is_spam_trap', 'risk_level', 'validated_at']
    search_fields = ['email', 'domain']
    ordering = ['-validated_at']
    readonly_fields = ['id', 'validated_at', 'score_breakdown']

    def status_badge(self, obj):
        colors = {
            'valid': 'green', 'invalid': 'red', 'risky': 'orange',
            'disposable': 'purple', 'spam_trap': 'darkred', 'catch_all': 'blue', 'unknown': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'


@admin.register(BulkValidationJob)
class BulkJobAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'status', 'total_emails', 'processed_emails', 'progress', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['original_filename', 'user__email']
    readonly_fields = ['id', 'created_at', 'started_at', 'completed_at', 'celery_task_id']

    def progress(self, obj):
        return f'{obj.progress_percentage}%'


@admin.register(DisposableDomain)
class DisposableDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'source', 'is_active', 'added_at']
    list_filter = ['is_active', 'source']
    search_fields = ['domain']
    actions = ['activate', 'deactivate']

    def activate(self, request, queryset):
        queryset.update(is_active=True)
        from apps.validation.engine.disposable_checker import invalidate_disposable_cache
        invalidate_disposable_cache()

    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
        from apps.validation.engine.disposable_checker import invalidate_disposable_cache
        invalidate_disposable_cache()


@admin.register(SpamTrapDomain)
class SpamTrapDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'confidence', 'is_active', 'added_at']
    list_filter = ['is_active']
    search_fields = ['domain']
