from chalice import Blueprint
from chalicelib.services.MemberService import member_service
from chalicelib.decorators import auth

members_api = Blueprint(__name__)


@members_api.route("/members", methods=["GET"], cors=True)
@auth(members_api, roles=["admin", "member"])
def get_all_members():
    """Fetches all members who have access to WhyPhi."""
    return member_service.get_all()


@members_api.route("/members/onboard/{user_id}", methods=["POST"], cors=True)
@auth(members_api, roles=[])
def onboard_member(user_id):
    data = members_api.current_request.json_body
    data["isNewUser"] = False

    if member_service.onboard(user_id, data):
        return {
            "status": True,
            "message": "User updated successfully.",
        }
    else:
        { "status": False}
