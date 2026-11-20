from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler


def custom_exception_handler(exc, context):
    """Translate Django ValidationError into a DRF 400 response."""
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            data = exc.message_dict
        else:
            data = {"detail": exc.messages}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    response = drf_handler(exc, context)
    return response
