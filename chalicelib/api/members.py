from chalice import Blueprint
from chalicelib.services.MemberService import member_service
from chalicelib.decorators import auth

members_api = Blueprint(__name__)


@members_api.route("/members", methods=["GET"], cors=True)
@auth(members_api, roles=["admin", "member"])
def get_all_members():
    """Get an applicant from <applicant_id>"""
    return member_service.get_all()
