from django.contrib import admin
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'key_prefix', 'permissions', 'is_active', 'total_requests', 'last_used_at']
    list_filter = ['permissions', 'is_active']
    search_fields = ['user__email', 'name', 'key_prefix']
    readonly_fields = ['id', 'key_hash', 'key_prefix', 'created_at', 'last_used_at', 'total_requests']
