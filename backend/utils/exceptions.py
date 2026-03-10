"""Custom exception handling for the SurveyLab API."""
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error response format.

    Response format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": {...}  // optional
        }
    }
    """
    # Call DRF's default handler first
    response = exception_handler(exc, context)

    if response is not None:
        error_data = _format_error_response(exc, response)
        response.data = error_data
        return response

    # Handle Django validation errors not caught by DRF
    if isinstance(exc, DjangoValidationError):
        error_data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed.",
                "details": exc.message_dict
                if hasattr(exc, "message_dict")
                else {"non_field_errors": exc.messages},
            }
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    # Log unhandled exceptions
    view = context.get("view")
    logger.error(
        f"Unhandled exception in {view.__class__.__name__ if view else 'unknown'}: "
        f"{type(exc).__name__}: {exc}",
        exc_info=True,
    )

    return None


def _format_error_response(exc, response):
    """Format the error response into a consistent structure."""
    error_code = _get_error_code(response.status_code)

    if isinstance(exc, DRFValidationError):
        return {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request data failed validation.",
                "details": response.data,
            }
        }

    if isinstance(response.data, dict):
        message = response.data.get("detail", str(exc))
        details = {
            k: v for k, v in response.data.items() if k != "detail"
        }
    elif isinstance(response.data, list):
        message = response.data[0] if response.data else str(exc)
        details = {}
    else:
        message = str(response.data)
        details = {}

    result = {
        "error": {
            "code": error_code,
            "message": str(message),
        }
    }

    if details:
        result["error"]["details"] = details

    return result


def _get_error_code(status_code):
    """Map HTTP status codes to error codes."""
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
    }
    return code_map.get(status_code, "UNKNOWN_ERROR")


class SurveyLabException(APIException):
    """Base exception for SurveyLab-specific errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A survey lab error occurred."
    default_code = "surveylab_error"


class SurveyQuotaExceeded(SurveyLabException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This survey has reached its maximum number of responses."
    default_code = "quota_exceeded"


class SurveyNotPublished(SurveyLabException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This survey is not currently accepting responses."
    default_code = "survey_not_published"


class DuplicateResponseError(SurveyLabException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "You have already submitted a response to this survey."
    default_code = "duplicate_response"


class ExportError(SurveyLabException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An error occurred while generating the export."
    default_code = "export_error"
