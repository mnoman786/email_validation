from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from .models import User, EmailVerificationToken, PasswordResetToken, AuditLog
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@extend_schema(tags=['auth'])
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        AuditLog.objects.create(
            user=user,
            action='register',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        return Response({
            'success': True,
            'message': 'Registration successful. Please verify your email.',
            'user': UserSerializer(user).data,
            'tokens': tokens,
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['auth'])
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        tokens = get_tokens_for_user(user)
        AuditLog.objects.create(
            user=user,
            action='login',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        from apps.billing.serializers import SubscriptionSerializer
        subscription = user.subscription if hasattr(user, 'subscription') else None
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'subscription': SubscriptionSerializer(subscription).data if subscription else None,
        })


@extend_schema(tags=['auth'])
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            AuditLog.objects.create(
                user=request.user,
                action='logout',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        except Exception:
            pass
        return Response({'success': True, 'message': 'Logged out successfully'})


@extend_schema(tags=['auth'])
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        from apps.billing.serializers import SubscriptionSerializer
        subscription = user.subscription if hasattr(user, 'subscription') else None
        return Response({
            'user': UserSerializer(user).data,
            'subscription': SubscriptionSerializer(subscription).data if subscription else None,
        })


@extend_schema(tags=['auth'])
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        AuditLog.objects.create(
            user=request.user,
            action='password_change',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        return Response({'success': True, 'message': 'Password changed successfully'})


@extend_schema(tags=['auth'])
class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            # TODO: Send email with reset link
        except User.DoesNotExist:
            pass
        return Response({'success': True, 'message': 'If that email exists, a reset link has been sent'})


@extend_schema(tags=['auth'])
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.context['reset_token']
        token.user.set_password(serializer.validated_data['new_password'])
        token.user.save()
        token.is_used = True
        token.save()
        return Response({'success': True, 'message': 'Password reset successfully'})


@extend_schema(tags=['auth'])
class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            vt = EmailVerificationToken.objects.get(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            vt.user.is_verified = True
            vt.user.save()
            vt.is_used = True
            vt.save()
            return Response({'success': True, 'message': 'Email verified successfully'})
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
