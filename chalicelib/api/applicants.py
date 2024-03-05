from chalice import Blueprint
from chalicelib.services.ApplicantService import applicant_service
from chalicelib.handlers.error_handler import handle_exceptions
from chalicelib.decorators import auth
from chalicelib.models.roles import Roles

from pydantic import ValidationError

applicants_api = Blueprint(__name__)


@applicants_api.route("/applicant/{id}", methods=["GET"], cors=True)
@auth(applicants_api, roles=[Roles.ADMIN, Roles.MEMBER])
def get_applicant(id):
    """Get an applicant from <applicant_id>"""
    return applicant_service.get(id)


@applicants_api.route("/applicants", methods=["GET"], cors=True)
@auth(applicants_api, roles=[Roles.ADMIN, Roles.MEMBER])
def get_applicants():
    return applicant_service.get_all()


@applicants_api.route("/applicants/{listing_id}", methods=["GET"], cors=True)
@auth(applicants_api, roles=[Roles.ADMIN, Roles.MEMBER])
def get_all_applicants(listing_id):
    """Gets all applicants from <listing_id>"""
    return applicant_service.get_all_from_listing(listing_id)
