from chalice import Blueprint
from chalicelib.services.MemberService import member_service
from chalicelib.decorators import auth
from chalicelib.models.roles import Roles

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


@members_api.route("/members", methods=["POST"], cors=True)
@auth(members_api, roles=[Roles.ADMIN])
def create_member():
    data = members_api.current_request.json_body
    return member_service.create(data)

@members_api.route("/members", methods=["DELETE"], cors=True)
@auth(members_api, roles=[Roles.ADMIN])
def delete_members():
    data = members_api.current_request.json_body
    return member_service.delete(data)

@members_api.route("/members/{user_id}/roles", methods=["PATCH"], cors=True)
@auth(members_api, roles=[Roles.ADMIN])
def update_member_roles(user_id):
    data = members_api.current_request.json_body
    return member_service.update_roles(user_id, data["roles"])