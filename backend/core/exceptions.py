from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'error': {
                'status_code': response.status_code,
                'message': '',
                'details': response.data,
            }
        }

        if response.status_code == 400:
            error_data['error']['message'] = 'Validation error'
        elif response.status_code == 401:
            error_data['error']['message'] = 'Authentication required'
        elif response.status_code == 403:
            error_data['error']['message'] = 'Permission denied'
        elif response.status_code == 404:
            error_data['error']['message'] = 'Resource not found'
        elif response.status_code == 429:
            error_data['error']['message'] = 'Rate limit exceeded'
        else:
            error_data['error']['message'] = 'An error occurred'

        response.data = error_data

    return response


class InsufficientCreditsError(Exception):
    pass


class ValidationError(Exception):
    pass


class APIKeyError(Exception):
    pass
