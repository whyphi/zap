from chalice.app import Request
from chalice.test import Client
from unittest.mock import MagicMock, patch

from chalice import NotFoundError, BadRequestError


from app import app

SAMPLE_INTERVIEW_LISTINGS = [
    {
        "_id": "1",
        "deadline": "2023-09-19T04:00:00.000Z",
        "dateCreated": "2023-09-15T17:03:29.156Z",
        "questions": [
            {
                "question": "Tell us about yourself. What are you passionate about/what motivates you? (200 words max)",
                "additional": "",
            },
        ],
        "title": "PCT Fall 2023 Rush Application",
        "semester": "fall",
        "isVisible": True,
        "active": True,
        "type": "Case",
        "response_ids": [],
    },
    {
        "_id": "2",
        "deadline": "2023-10-19T04:00:00.000Z",
        "dateCreated": "2023-10-15T17:03:29.156Z",
        "questions": [
            {
                "question": "test",
                "additional": "",
            },
        ],
        "title": "PCT Spring 2023 Rush Application",
        "semester": "spring",
        "isVisible": True,
        "active": True,
        "type": "Case",
        "response_ids": [],
    },
]


def test_create_interview():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.InterviewService.interview_service.create_interview"
            ) as mock_create:
                mock_create.return_value = {"msg": True}
                response = client.http.post(
                    f"/interviews",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}


def test_get_interview_listing():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.InterviewService.interview_service.get_interview_listing"
            ) as mock_get:
                mock_get.return_value = SAMPLE_INTERVIEW_LISTINGS[0]
                response = client.http.get(
                    f"/interviews/{SAMPLE_INTERVIEW_LISTINGS[0]['_id']}",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == SAMPLE_INTERVIEW_LISTINGS[0]


def test_get_all_interviews():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.InterviewService.interview_service.get_all_interviews"
            ) as mock_get:
                mock_get.return_value = SAMPLE_INTERVIEW_LISTINGS
                response = client.http.get(
                    f"/interviews",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == SAMPLE_INTERVIEW_LISTINGS


def test_delete_nonexisting_interview_listing():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.InterviewService.interview_service.delete_interview_listing"
            ) as mock_delete:
                mock_delete.side_effect = NotFoundError(
                    "Interview Listing does not exist."
                )
                response = client.http.delete(
                    f"/interviews/'nonexistent123'",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 404


def test_delete_interview_listing():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.InterviewService.interview_service.delete_interview_listing"
            ) as mock_delete:
                mock_delete.return_value = {
                    "message": f"Interview Listing with ID {SAMPLE_INTERVIEW_LISTINGS[0]['_id']} and its associated responses have been successfully deleted."
                }
                response = client.http.delete(
                    f"/interviews/{SAMPLE_INTERVIEW_LISTINGS[0]['_id']}",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {
                    "message": f"Interview Listing with ID {SAMPLE_INTERVIEW_LISTINGS[0]['_id']} and its associated responses have been successfully deleted."
                }
