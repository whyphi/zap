from chalice.app import NotFoundError, BadRequestError, ChaliceViewError, Response
import logging
from typing import Callable, Any

# Generic client-side errors
GENERIC_CLIENT_ERROR = "Invalid input. Please check your request and try again."


def handle_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except BadRequestError as e:
            logging.warning(f"[{func.__name__}] BadRequestError: {str(e)}")
            raise

        except NotFoundError as e:
            logging.warning(f"[{func.__name__}] NotFoundError: {str(e)}")
            raise

        except ChaliceViewError as e:
            logging.error(f"[{func.__name__}] ChaliceViewError: {str(e)}")
            raise

        except Exception as e:
            logging.exception(f"[{func.__name__}] Unexpected error: {str(e)}")
            return Response(
                body={"error": "Internal Server Error", "message": str(e)},
                headers={"Content-Type": "application/json"},
                status_code=500,
            )

    return wrapper
