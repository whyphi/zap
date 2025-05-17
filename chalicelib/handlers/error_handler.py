from chalice import Response
from chalice import NotFoundError, BadRequestError
import logging


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except BadRequestError as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            raise BadRequestError(str(e))

        except NotFoundError as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            raise NotFoundError(str(e))

        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return Response(
                body=f"An unexpected error occurred: {str(e)}",
                headers={"Content-Type": "application/json"},
                status_code=500,
            )

    return wrapper
