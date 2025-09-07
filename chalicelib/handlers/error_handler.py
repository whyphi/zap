from chalice.app import NotFoundError, BadRequestError, ChaliceViewError, Response
import logging
from typing import Callable, Any
from functools import wraps
from postgrest.exceptions import APIError


# Generic client-side errors
GENERIC_CLIENT_ERROR = "Invalid input. Please check your request and try again."

logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for Chalice route handlers.

    - Logs and re-raises known Chalice errors (`BadRequestError`, `NotFoundError`,
      `ChaliceViewError`) so that Chalice can convert them into proper HTTP responses.
    - Logs unexpected exceptions and returns a generic
      `500 Internal Server Error` JSON response.
    - Ensures API clients always receive a well-formed HTTP response.

    Args:
        func (Callable): The route handler function to wrap.

    Returns:
        Callable: The wrapped function with exception handling applied.
    """

    @wraps(func)  # preserves metadata like __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except BadRequestError as e:
            logger.warning(f"[{func.__qualname__}] BadRequestError: {str(e)}")
            raise

        except NotFoundError as e:
            logger.warning(f"[{func.__qualname__}] NotFoundError: {str(e)}")
            raise

        except ChaliceViewError as e:
            logger.error(f"[{func.__qualname__}] ChaliceViewError: {str(e)}")
            raise

        except Exception as e:
            logger.exception(f"[{func.__qualname__}] Unexpected error: {str(e)}")
            return Response(
                body={"error": "Internal Server Error", "message": str(e)},
                headers={"Content-Type": "application/json"},
                status_code=500,
            )

    return wrapper


def log_and_reraise(func):
    """
    Decorator for repository-layer functions.

    - Logs Supabase `APIError` exceptions with context, then re-raises them
      so the service layer can handle them appropriately.
    - Logs and re-raises any other unexpected exceptions.
    - Does NOT convert exceptions into HTTP responses — this is left for the
      service or route layers to decide.

    Args:
        func (Callable): The repository function to wrap.

    Returns:
        Callable: The wrapped function with logging applied.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.error(
                f"[{func.__qualname__}] Supabase APIError: {e.message}", exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"[{func.__qualname__}] Unexpected error: {str(e)}", exc_info=True
            )
            raise

    return wrapper
