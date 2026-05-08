import django_filters
from .models import ValidationResult, BulkValidationJob


class ValidationResultFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    domain = django_filters.CharFilter(field_name='domain', lookup_expr='icontains')
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte')
    is_disposable = django_filters.BooleanFilter()
    is_catch_all = django_filters.BooleanFilter()
    is_role_account = django_filters.BooleanFilter()
    is_spam_trap = django_filters.BooleanFilter()
    validated_after = django_filters.DateTimeFilter(field_name='validated_at', lookup_expr='gte')
    validated_before = django_filters.DateTimeFilter(field_name='validated_at', lookup_expr='lte')

    class Meta:
        model = ValidationResult
        fields = [
            'status', 'domain', 'score_min', 'score_max',
            'is_disposable', 'is_catch_all', 'is_role_account', 'is_spam_trap',
            'validated_after', 'validated_before',
        ]


class BulkJobFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = BulkValidationJob
        fields = ['status', 'created_after', 'created_before']
