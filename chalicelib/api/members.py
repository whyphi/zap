from chalice import Blueprint
from chalicelib.services.MemberService import member_service

members_api = Blueprint(__name__)


@members_api.route("/members", methods=["GET"], cors=True)
def get_all_members():
    """Get an applicant from <applicant_id>"""
    return member_service.get_all()
