from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import APIKey
from .serializers import APIKeySerializer, CreateAPIKeySerializer, APIKeyCreatedSerializer
from apps.accounts.models import AuditLog


@extend_schema(tags=['api-keys'])
class APIKeyListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateAPIKeySerializer
        return APIKeySerializer

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CreateAPIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Limit API keys per user
        if self.get_queryset().filter(is_active=True).count() >= 10:
            return Response(
                {'error': {'message': 'Maximum 10 API keys allowed'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key, raw_key = APIKey.create_key(
            user=request.user,
            name=serializer.validated_data['name'],
            permissions=serializer.validated_data.get('permissions', 'validate'),
            expires_at=serializer.validated_data.get('expires_at'),
            allowed_ips=serializer.validated_data.get('allowed_ips', []),
            rate_limit_per_hour=serializer.validated_data.get('rate_limit_per_hour', 1000),
        )

        AuditLog.objects.create(
            user=request.user,
            action='api_key_create',
            description=f'Created API key: {api_key.name}',
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response({
            'success': True,
            'api_key': {
                'id': str(api_key.id),
                'name': api_key.name,
                'key': raw_key,
                'key_prefix': api_key.key_prefix,
                'permissions': api_key.permissions,
                'created_at': api_key.created_at.isoformat(),
            },
            'warning': 'Save your API key now. It will not be shown again.',
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['api-keys'])
class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        AuditLog.objects.create(
            user=request.user,
            action='api_key_delete',
            description=f'Deleted API key: {instance.name}',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response({'success': True, 'message': 'API key deactivated'})
