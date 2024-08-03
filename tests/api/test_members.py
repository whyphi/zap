from chalice.test import Client
from unittest.mock import patch
from chalice.config import Config
from chalice.local import LocalGateway

from app import app
import json


lg = LocalGateway(app, Config())


TEST_MEMBER_DATA = [
    {
        "_id": "12a34bc678df27ead9388708",
        "name": "Name Name",
        "email": "whyphi@bu.edu",
        "class": "Lambda",
        "college": "CAS",
        "family": "Poseidon",
        "graduationYear": "2026",
        "isEboard": "no",
        "major": "Computer Science",
        "minor": "",
        "isNewUser": False,
        "team": "technology",
        "roles": ["admin", "eboard", "member"],
        "big": "Name Name",
    },
    {
        "_id": "12a34bc678df27ead9388709",
        "name": "Name Name",
        "email": "whyphi1@bu.edu",
        "class": "Lambda",
        "college": "QST",
        "family": "Atlas",
        "graduationYear": "2027",
        "isEboard": "no",
        "major": "Business Administration",
        "minor": "",
        "isNewUser": True,
        "team": "operations",
        "roles": ["member"],
        "big": "Name Name",
    },
]


def test_get_member():
    # Create a Chalice test client
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            mock_decode.return_value = {"role": "member"}

            with patch(
                "chalicelib.services.MemberService.member_service.get_by_id"
            ) as mock_get:
                mock_get.return_value = TEST_MEMBER_DATA[0]
                response = client.http.get(
                    f"/member/{TEST_MEMBER_DATA[0]['_id']}",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )
                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == TEST_MEMBER_DATA[0]


def test_get_member_non_existent():
    # Create a Chalice test client
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            mock_decode.return_value = {"role": "member"}

            with patch(
                "chalicelib.services.MemberService.member_service.get_by_id"
            ) as mock_get:
                mock_get.return_value = {}
                response = client.http.get(
                    "/member/123",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )
                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == {}


def test_update_member():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            mock_decode.return_value = {"role": "member"}

            with patch(
                "chalicelib.services.MemberService.member_service.update"
            ) as mock_update:
                # Make copy of TEST_MEMBER_DATA[0]
                update_member_data = TEST_MEMBER_DATA[0].copy()
                update_member_data["name"] = "New Name"
                mock_update.return_value = update_member_data

                response = client.http.put(
                    f"/member/{TEST_MEMBER_DATA[0]['_id']}",
                    body=update_member_data,
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )
                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == update_member_data


def test_get_all_members():
    # Create a Chalice test client
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            mock_decode.return_value = {"role": "member"}

            with patch(
                "chalicelib.services.MemberService.member_service.get_all"
            ) as mock_get_all:
                mock_get_all.return_value = TEST_MEMBER_DATA
                response = client.http.get(
                    "/members",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )
                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == TEST_MEMBER_DATA


def test_onboard_member():
    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"role": "member"}

        with patch(
            "chalicelib.services.MemberService.member_service.onboard"
        ) as mock_onboard:
            mock_onboard.return_value = True

            # Utilize local gateway for passing in body
            response = lg.handle_request(
                method="POST",
                path=f"/members/onboard/{TEST_MEMBER_DATA[1]['_id']}",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                },
                body=json.dumps(TEST_MEMBER_DATA[1]),
            )

            # Check the response status code and body
            assert response["statusCode"] == 200
            assert json.loads(response["body"]) == {
                "status": True,
                "message": "User updated successfully.",
            }


def test_onboard_member_fail_on_mongo():
    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"role": "member"}

        with patch(
            "chalicelib.services.MemberService.member_service.onboard"
        ) as mock_onboard:
            mock_onboard.return_value = False
            response = lg.handle_request(
                method="POST",
                path=f"/members/onboard/{TEST_MEMBER_DATA[1]['_id']}",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                },
                body=json.dumps(TEST_MEMBER_DATA[1]),
            )
            print(response)
            # Check the response status code and body
            assert response["statusCode"] == 200
            assert json.loads(response["body"]) == {
                "status": False,
            }


def test_create_member():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            mock_decode.return_value = {"role": "admin"}

            with patch(
                "chalicelib.services.MemberService.member_service.create"
            ) as mock_create:
                mock_create.return_value = {
                    "success": True,
                    "message": "User created successfully",
                }
                response = client.http.post(
                    "/members",
                    body=json.dumps(TEST_MEMBER_DATA[0]),
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )
                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == {
                    "success": True,
                    "message": "User created successfully",
                }


def test_delete_members():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            mock_decode.return_value = {"role": "admin"}

            with patch(
                "chalicelib.services.MemberService.member_service.delete"
            ) as mock_delete:
                mock_delete.return_value = {
                    "success": True,
                    "message": "Documents deleted successfully",
                }
                response = client.http.delete(
                    "/members",
                    body=json.dumps(TEST_MEMBER_DATA),
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )
                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == {
                    "success": True,
                    "message": "Documents deleted successfully",
                }


def test_update_member_roles():
    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"role": "admin"}

        with patch(
            "chalicelib.services.MemberService.member_service.update_roles"
        ) as mock_update:
            update_member_data = TEST_MEMBER_DATA[0].copy()
            update_member_data["roles"] = ["admin"]
            mock_update.return_value = update_member_data

            response = lg.handle_request(
                method="PATCH",
                path=f"/members/{TEST_MEMBER_DATA[0]['_id']}/roles",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                },
                body=json.dumps(update_member_data),
            )

            print(response)
            # Check the response status code and body
            assert response["statusCode"] == 200
            assert json.loads(response["body"]) == update_member_data
