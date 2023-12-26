from chalice import NotFoundError, BadRequestError


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except BadRequestError as e:
            return {"status": False, "message": str(e)}, 400

        except NotFoundError as e:
            return {"status": False, "message": str(e)}, 404

        except Exception as e:
            return {"status": False, "message": "Internal Server Error"}, 500

    return wrapper