import os
import csv
import io
import logging
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import ValidationResult, BulkValidationJob
from .serializers import (
    ValidationResultSerializer, ValidateSingleEmailSerializer,
    BulkJobSerializer, BulkUploadSerializer, ValidationStatsSerializer
)
from .engine import EmailValidator
from .filters import ValidationResultFilter, BulkJobFilter
from core.permissions import IsOwner

logger = logging.getLogger(__name__)


@extend_schema(tags=['validation'])
class ValidateSingleEmailView(generics.GenericAPIView):
    serializer_class = ValidateSingleEmailSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        check_smtp = serializer.validated_data.get('check_smtp', True)

        # Deduct credits
        subscription = getattr(request.user, 'subscription', None)
        if subscription and not request.user.is_staff:
            if subscription.available_credits < 1:
                return Response(
                    {'error': {'message': 'Insufficient credits', 'credits': 0}},
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
            subscription.use_credits(1)

        validator = EmailValidator(check_smtp=check_smtp)
        validation_data = validator.validate(email)

        result = ValidationResult(
            user=request.user,
            email=validation_data.email,
            original_email=validation_data.original_email or email,
            status=validation_data.status,
            score=validation_data.score,
            is_valid=validation_data.is_valid,
            local_part=validation_data.local_part,
            domain=validation_data.domain,
            syntax_valid=validation_data.syntax_valid,
            mx_found=validation_data.mx_found,
            mx_records=validation_data.mx_records,
            dns_valid=validation_data.dns_valid,
            smtp_check=validation_data.smtp_check,
            smtp_connectable=validation_data.smtp_connectable,
            smtp_response_code=validation_data.smtp_response_code,
            is_disposable=validation_data.is_disposable,
            is_catch_all=validation_data.is_catch_all,
            is_role_account=validation_data.is_role_account,
            is_free_provider=validation_data.is_free_provider,
            is_spam_trap=validation_data.is_spam_trap,
            is_greylisted=validation_data.is_greylisted,
            domain_reputation=validation_data.domain_reputation,
            risk_level=validation_data.risk_level,
            suggested_action=validation_data.suggested_action,
            score_breakdown=validation_data.score_breakdown,
            processing_time_ms=validation_data.processing_time_ms,
            api_source='api' if hasattr(request, 'api_key') else 'web',
        )
        result.save()

        return Response({
            'success': True,
            'result': result.to_api_response(),
        })


@extend_schema(tags=['validation'])
class ValidationHistoryView(generics.ListAPIView):
    serializer_class = ValidationResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ValidationResultFilter
    search_fields = ['email', 'domain']
    ordering_fields = ['validated_at', 'score', 'status']
    ordering = ['-validated_at']

    def get_queryset(self):
        return ValidationResult.objects.filter(
            user=self.request.user,
            bulk_job__isnull=True
        )


@extend_schema(tags=['validation'])
class ValidationStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ValidationResult.objects.filter(user=request.user)

        # Date filter
        days = int(request.query_params.get('days', 30))
        if days > 0:
            from datetime import timedelta
            since = timezone.now() - timedelta(days=days)
            qs = qs.filter(validated_at__gte=since)

        stats = qs.aggregate(
            total=Count('id'),
            valid=Count('id', filter=Q(status='valid')),
            invalid=Count('id', filter=Q(status='invalid')),
            risky=Count('id', filter=Q(status='risky')),
            disposable=Count('id', filter=Q(status='disposable')),
            catch_all=Count('id', filter=Q(status='catch_all')),
            spam_trap=Count('id', filter=Q(status='spam_trap')),
            unknown=Count('id', filter=Q(status='unknown')),
            avg_score=Avg('score'),
        )

        total = stats['total'] or 1
        bulk_jobs = BulkValidationJob.objects.filter(user=request.user).count()

        # Daily breakdown for chart
        from django.db.models.functions import TruncDate
        daily_stats = (
            qs.annotate(date=TruncDate('validated_at'))
            .values('date')
            .annotate(count=Count('id'), avg_score=Avg('score'))
            .order_by('date')
        )

        return Response({
            'overview': {
                'total_validations': stats['total'],
                'valid_count': stats['valid'],
                'invalid_count': stats['invalid'],
                'risky_count': stats['risky'],
                'disposable_count': stats['disposable'],
                'catch_all_count': stats['catch_all'],
                'spam_trap_count': stats['spam_trap'],
                'unknown_count': stats['unknown'],
                'average_score': round(stats['avg_score'] or 0, 1),
                'valid_percentage': round((stats['valid'] / total) * 100, 1),
                'total_bulk_jobs': bulk_jobs,
            },
            'daily_breakdown': list(daily_stats),
        })


@extend_schema(tags=['bulk'])
class BulkJobViewSet(viewsets.ModelViewSet):
    serializer_class = BulkJobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BulkJobFilter
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return BulkValidationJob.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = BulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        name = serializer.validated_data.get('name', uploaded_file.name)

        # Count emails
        content = uploaded_file.read().decode('utf-8', errors='ignore')
        emails = self._extract_emails_from_csv(content)

        if not emails:
            return Response(
                {'error': {'message': 'No valid emails found in file'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        max_emails = getattr(settings, 'MAX_BULK_EMAILS', 500000)
        if len(emails) > max_emails:
            return Response(
                {'error': {'message': f'Maximum {max_emails} emails per upload'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check credits
        subscription = getattr(request.user, 'subscription', None)
        if subscription and not request.user.is_staff:
            if subscription.available_credits < len(emails):
                return Response(
                    {
                        'error': {
                            'message': 'Insufficient credits',
                            'required': len(emails),
                            'available': subscription.available_credits
                        }
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
            subscription.use_credits(len(emails))

        # Save file
        import uuid as uuid_mod
        file_dir = os.path.join(settings.MEDIA_ROOT, 'bulk_uploads', str(request.user.id))
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, f'{uuid_mod.uuid4()}.csv')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(emails))

        job = BulkValidationJob.objects.create(
            user=request.user,
            name=name,
            original_filename=uploaded_file.name,
            file_path=file_path,
            total_emails=len(emails),
            status='pending',
        )

        # Dispatch Celery task
        from .tasks import process_bulk_validation
        task = process_bulk_validation.delay(str(job.id))
        job.celery_task_id = task.id
        job.save(update_fields=['celery_task_id'])

        return Response({
            'success': True,
            'message': f'Bulk job created. Processing {len(emails)} emails.',
            'job': BulkJobSerializer(job).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        job = self.get_object()
        results = ValidationResult.objects.filter(bulk_job=job)

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            results = results.filter(status=status_filter)

        from core.pagination import StandardResultsSetPagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(results, request)
        return paginator.get_paginated_response(ValidationResultSerializer(page, many=True).data)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        job = self.get_object()
        if job.status != 'completed':
            return Response(
                {'error': {'message': 'Job not completed yet'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        status_filter = request.query_params.get('status', 'all')
        results = ValidationResult.objects.filter(bulk_job=job)
        if status_filter != 'all':
            results = results.filter(status=status_filter)

        def generate_csv():
            headers = [
                'email', 'status', 'score', 'is_valid', 'mx_found',
                'smtp_check', 'is_disposable', 'is_catch_all', 'is_role_account',
                'is_free_provider', 'is_spam_trap', 'domain_reputation',
                'risk_level', 'suggested_action', 'domain',
            ]
            yield ','.join(headers) + '\n'
            for r in results.iterator(chunk_size=1000):
                row = [
                    r.email, r.status, str(r.score), str(r.is_valid),
                    str(r.mx_found), str(r.smtp_check), str(r.is_disposable),
                    str(r.is_catch_all), str(r.is_role_account), str(r.is_free_provider),
                    str(r.is_spam_trap), r.domain_reputation, r.risk_level,
                    r.suggested_action, r.domain,
                ]
                yield ','.join(row) + '\n'

        response = StreamingHttpResponse(generate_csv(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="results_{job.id}.csv"'
        return response

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        job = self.get_object()
        if job.status in ('completed', 'failed', 'cancelled'):
            return Response({'error': {'message': 'Job cannot be cancelled'}}, status=status.HTTP_400_BAD_REQUEST)

        if job.celery_task_id:
            from config.celery import app as celery_app
            celery_app.control.revoke(job.celery_task_id, terminate=True)

        job.status = 'cancelled'
        job.save(update_fields=['status'])
        return Response({'success': True, 'message': 'Job cancelled'})

    def _extract_emails_from_csv(self, content: str) -> list:
        emails = []
        seen = set()
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            for cell in row:
                cell = cell.strip().strip('"').strip("'").lower()
                if '@' in cell and cell not in seen and len(cell) <= 512:
                    seen.add(cell)
                    emails.append(cell)
        return emails
