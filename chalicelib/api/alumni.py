from chalice import Blueprint
from chalicelib.services.AlumniService import alumni_service
from chalicelib.handlers.error_handler import handle_exceptions
from pydantic import ValidationError

alumni_api = Blueprint(__name__)


@alumni_api.route("/alumni", methods=["POST"], cors=True)
def create_alumni():
    """Creates a new alumni with given information"""
    return alumni_service.create(alumni_api.current_request.json_body)


@alumni_api.route("/alumni", methods=["GET"], cors=True)
def get_all_alumni():
    """Gets all alumni available"""
    return alumni_service.get_all()


@alumni_api.route("/alumni/{id}", methods=["DELETE"], cors=True)
def delete_alumni(id):
    """Deletes a alumni with the given ID."""
    return alumni_service.delete(id)


@alumni_api.route("/alumni/{id}/update-field", methods=["PATCH"], cors=True)
@handle_exceptions
def update_alumni_field_route(id):
    try:
        alumni_service.update_field_route(id, alumni_api.current_request.json_body)

    except ValidationError as e:
        return {"status": False, "message": str(e)}, 400
