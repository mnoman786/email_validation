from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    keyword = 'Api-Key'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith(f'{self.keyword} '):
            # Also check X-API-Key header
            raw_key = request.META.get('HTTP_X_API_KEY', '')
            if not raw_key:
                return None
        else:
            raw_key = auth_header[len(self.keyword) + 1:]

        if not raw_key:
            return None

        api_key = APIKey.authenticate(raw_key)
        if not api_key:
            raise AuthenticationFailed('Invalid or expired API key')

        if not api_key.user.is_active:
            raise AuthenticationFailed('User account is disabled')

        # IP whitelist check
        if api_key.allowed_ips:
            client_ip = self._get_client_ip(request)
            if client_ip not in api_key.allowed_ips:
                raise AuthenticationFailed('IP not allowed')

        api_key.record_usage()
        request.api_key = api_key
        return (api_key.user, api_key)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
