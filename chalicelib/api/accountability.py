from chalice.app import Blueprint
from chalicelib.decorators import auth
from chalicelib.services.AccountabilityService import accountability_service
from chalicelib.models.roles import Roles

accountability_api = Blueprint(__name__)


@accountability_api.route("/accountability", methods=["GET"], cors=True)
@auth(accountability_api, roles=[Roles.ADMIN, Roles.MEMBER])
def get_accountability():
    if accountability_api.current_request.query_params:
        page = int(accountability_api.current_request.query_params.get("page", 0))
        page_size = int(
            accountability_api.current_request.query_params.get("page_size", 20)
        )
    else:
        page, page_size = 0, 20
    return accountability_service.get_total_accountability(page, page_size)
