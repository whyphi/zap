from chalice import Blueprint
from chalicelib.decorators import auth
from chalicelib.services.InterviewService import interview_service

interviews_api = Blueprint(__name__)


@interviews_api.route("/interviews", methods=["POST"], cors=True)
@auth(interviews_api, roles=["admin"])
def create_interview():
    data = interviews_api.current_request.json_body
    return interview_service.create_interview(data)


@interviews_api.route("/interviews", methods=["GET"], cors=True)
@auth(interviews_api, roles=["admin"])
def get_all_interviews():
    return interview_service.get_all_interviews()


@interviews_api.route("/interviews/{interview_id}", methods=["GET"], cors=True)
@auth(interviews_api, roles=["admin"])
def get_interview_listing(interview_id: str):
    return interview_service.get_interview_listing(interview_id)


@interviews_api.route("/interviews/{interview_id}", methods=["DELETE"], cors=True)
@auth(interviews_api, roles=["admin"])
def delete_interview_listing(interview_id: str):
    return interview_service.delete_interview_listing(interview_id)
