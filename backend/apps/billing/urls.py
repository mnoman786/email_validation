from django.urls import path
from . import views

urlpatterns = [
    path('subscription/', views.SubscriptionDetailView.as_view(), name='subscription'),
    path('credit-packs/', views.CreditPackListView.as_view(), name='credit-packs'),
    path('plans/', views.PlansListView.as_view(), name='plans'),
    path('payments/', views.PaymentHistoryView.as_view(), name='payments'),
    path('checkout/', views.CreateCheckoutSessionView.as_view(), name='checkout'),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
]
