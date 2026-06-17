from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from .exceptions import AppException
from .middleware import get_current_trace_id

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    trace_id = get_current_trace_id()

    if isinstance(exc, AppException):
        return Response(
            {
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "fields": exc.fields,
                    "trace_id": trace_id
                }
            },
            status=exc.status_code
        )

    if response is not None:
        error_code = "internal_error"
        message = str(exc)
        fields = None

        if isinstance(exc, ValidationError):
            error_code = "validation_error"
            message = "Validation error"
            
            # Flattening fields: converting lists of messages to a single string
            fields = {}
            if isinstance(response.data, dict):
                for field, value in response.data.items():
                    if isinstance(value, list) and len(value) > 0:
                        fields[field] = str(value[0])
                    else:
                        fields[field] = str(value)
            else:
                fields = response.data
        elif hasattr(exc, 'default_code'):
             # Standard DRF exceptions have default_code
             error_code = getattr(exc, 'default_code', "internal_error")
             # Try to get a better message if possible
             if isinstance(response.data, dict) and 'detail' in response.data:
                 message = response.data['detail']
             elif isinstance(response.data, list) and len(response.data) > 0:
                 message = response.data[0]

        # Standardizing status codes as per requirements if they match
        # (The requirements list specific codes for specific statuses)
        
        # Mapping DRF default codes to required snake_case codes if they differ
        code_mapping = {
            "not_found": "not_found", # Usually specialized in AppException but good as fallback
            "permission_denied": "forbidden",
            "not_authenticated": "unauthorized",
            "authentication_failed": "invalid_credentials",
            "throttled": "too_many_requests",
        }
        
        error_code = code_mapping.get(error_code, error_code)

        response.data = {
            "error": {
                "code": error_code,
                "message": message,
                "fields": fields,
                "trace_id": trace_id
            }
        }
    else:
        # For non-DRF exceptions (500 Internal Server Error)
        response = Response(
            {
                "error": {
                    "code": "internal_error",
                    "message": str(exc) if hasattr(exc, 'message') else "Internal server error",
                    "fields": None,
                    "trace_id": trace_id
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
