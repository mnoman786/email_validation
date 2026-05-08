import stripe
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Subscription, CreditPack, Payment, PLAN_CONFIGS
from .serializers import (
    SubscriptionSerializer, CreditPackSerializer, PaymentSerializer,
    PurchaseCreditPackSerializer, UpgradePlanSerializer
)

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@extend_schema(tags=['billing'])
class SubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        sub, _ = Subscription.objects.get_or_create(
            user=self.request.user,
            defaults={'plan': 'free', 'available_credits': settings.DEFAULT_FREE_CREDITS}
        )
        return sub


@extend_schema(tags=['billing'])
class CreditPackListView(generics.ListAPIView):
    serializer_class = CreditPackSerializer
    permission_classes = [AllowAny]
    queryset = CreditPack.objects.filter(is_active=True)


@extend_schema(tags=['billing'])
class PaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


@extend_schema(tags=['billing'])
class CreateCheckoutSessionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseCreditPackSerializer

    def post(self, request):
        if not settings.STRIPE_SECRET_KEY:
            return Response({'error': {'message': 'Stripe not configured'}}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pack = CreditPack.objects.get(id=serializer.validated_data['credit_pack_id'], is_active=True)
        except CreditPack.DoesNotExist:
            return Response({'error': {'message': 'Credit pack not found'}}, status=status.HTTP_404_NOT_FOUND)

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        success_url = serializer.validated_data.get('success_url', f'{frontend_url}/billing?success=true')
        cancel_url = serializer.validated_data.get('cancel_url', f'{frontend_url}/billing?cancelled=true')

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': pack.name, 'description': f'{pack.credits:,} email verifications'},
                        'unit_amount': int(pack.price_usd * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=request.user.email,
                metadata={
                    'user_id': str(request.user.id),
                    'credit_pack_id': str(pack.id),
                    'credits': pack.credits,
                },
            )
            return Response({'checkout_url': session.url, 'session_id': session.id})
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error: {e}')
            return Response({'error': {'message': str(e)}}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['billing'])
class PlansListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        plans = []
        for key, config in PLAN_CONFIGS.items():
            plans.append({
                'id': key,
                'name': config['name'],
                'price': config['price'],
                'credits': config['credits'],
                'features': config['features'],
            })
        return Response({'plans': plans})


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error(f'Stripe webhook error: {e}')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            self._handle_checkout_complete(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            self._handle_invoice_paid(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            self._handle_subscription_cancelled(event['data']['object'])

        return Response({'received': True})

    def _handle_checkout_complete(self, session):
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        credits = int(metadata.get('credits', 0))
        credit_pack_id = metadata.get('credit_pack_id')

        if not user_id or not credits:
            return

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            sub = user.subscription
            sub.add_credits(credits)

            Payment.objects.create(
                user=user,
                subscription=sub,
                payment_type='credit_pack',
                status='succeeded',
                amount_usd=session.get('amount_total', 0) / 100,
                credits_added=credits,
                description=f'Credit pack purchase: {credits:,} credits',
                stripe_payment_intent_id=session.get('payment_intent', ''),
            )
            logger.info(f'Added {credits} credits to user {user_id}')
        except Exception as e:
            logger.error(f'Failed to process credit purchase: {e}')

    def _handle_invoice_paid(self, invoice):
        pass

    def _handle_subscription_cancelled(self, subscription):
        try:
            sub = Subscription.objects.get(stripe_subscription_id=subscription['id'])
            sub.status = 'cancelled'
            sub.save(update_fields=['status'])
        except Subscription.DoesNotExist:
            pass
