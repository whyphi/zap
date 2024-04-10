from chalice import Blueprint
from chalicelib.decorators import auth

accountability_api = Blueprint(__name__)


@accountability_api.route("/timeframes", methods=["POST"], cors=True)
@auth(accountability_api, roles=["admin"])
def get_accountability():
    return accountability_service.get_accountability()