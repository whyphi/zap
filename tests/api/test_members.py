import os

os.environ["CHALICE_TESTING"] = "1"

import json
import pytest
from chalice.test import Client
from unittest.mock import Mock, patch
from app import app
from chalicelib.api import members

TEST_MEMBER_DATA = [
    {
        "id": "12a34bc678df27ead9388708",
        "name": "Name Name",
        "email": "whyphi@bu.edu",
        "class": "Lambda",
        "college": "CAS",
        "family": "Poseidon",
        "grad_year": "2026",
        "is_eboard": "no",
        "major": "Computer Science",
        "minor": "",
        "is_new_user": False,
        "team": "technology",
        "roles": ["admin", "eboard", "member"],
        "big": "Name Name",
    },
    {
        "id": "12a34bc678df27ead9388709",
        "name": "Name Name",
        "email": "whyphi1@bu.edu",
        "class": "Lambda",
        "college": "QST",
        "family": "Atlas",
        "grad_year": "2027",
        "is_eboard": "no",
        "major": "Business Administration",
        "minor": "",
        "is_new_user": True,
        "team": "operations",
        "roles": ["member"],
        "big": "Name Name",
    },
]


@pytest.fixture(scope="module")
def test_client():
    mock_member_service = Mock()

    # Register routes with the mock service
    members.register_routes(member_service=mock_member_service)
    app.register_blueprint(members.members_api)

    with Client(app) as client:
        yield client, mock_member_service


def test_get_member(test_client):
    client, mock_service = test_client
    mock_service.get_by_id.return_value = TEST_MEMBER_DATA[0]

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["member"]}
        resp = client.http.get(
            f"/members/{TEST_MEMBER_DATA[0]['id']}",
            headers={"Authorization": "Bearer TOKEN"},
        )

    assert resp.status_code == 200
    assert resp.json_body == TEST_MEMBER_DATA[0]
    mock_service.get_by_id.assert_called_once_with(TEST_MEMBER_DATA[0]["id"])


def test_update_member(test_client):
    client, mock_service = test_client
    update_member_data = {**TEST_MEMBER_DATA[0], "name": "New Name"}
    mock_service.update.return_value = update_member_data

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["member"]}
        resp = client.http.put(
            f"/members/{TEST_MEMBER_DATA[0]['id']}",
            body=json.dumps(update_member_data),
            headers={
                "Authorization": "Bearer TOKEN",
                "Content-Type": "application/json",
            },
        )

    assert resp.status_code == 200
    assert resp.json_body == update_member_data
    mock_service.update.assert_called_once()


def test_get_all_members(test_client):
    client, mock_service = test_client
    mock_service.get_all.return_value = TEST_MEMBER_DATA

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        resp = client.http.get(
            "/members", headers={"Authorization": "Bearer TOKEN"}
        )

    assert resp.status_code == 200
    assert resp.json_body == TEST_MEMBER_DATA
    mock_service.get_all.assert_called_once()


def test_onboard_member(test_client):
    client, mock_service = test_client
    mock_service.onboard.return_value = True

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["member"]}
        resp = client.http.post(
            f"/members/onboard/{TEST_MEMBER_DATA[1]['id']}",
            body=json.dumps(TEST_MEMBER_DATA[1]),
            headers={
                "Authorization": "Bearer TOKEN",
                "Content-Type": "application/json",
            },
        )

    assert resp.status_code == 200
    assert resp.json_body == {
        "status": True,
        "message": "User updated successfully.",
    }
    mock_service.onboard.assert_called_once()


def test_create_member(test_client):
    client, mock_service = test_client
    mock_service.create.return_value = {
        "success": True,
        "message": "User created successfully",
    }

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        resp = client.http.post(
            "/members",
            body=json.dumps(TEST_MEMBER_DATA[0]),
            headers={
                "Authorization": "Bearer TOKEN",
                "Content-Type": "application/json",
            },
        )

    assert resp.status_code == 200
    assert resp.json_body == {
        "success": True,
        "message": "User created successfully",
    }
    mock_service.create.assert_called_once()


def test_delete_members(test_client):
    client, mock_service = test_client
    mock_service.delete.return_value = {
        "success": True,
        "message": "Documents deleted successfully",
    }

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        resp = client.http.delete(
            "/members",
            body=json.dumps(TEST_MEMBER_DATA),
            headers={
                "Authorization": "Bearer TOKEN",
                "Content-Type": "application/json",
            },
        )

    assert resp.status_code == 200
    assert resp.json_body == {
        "success": True,
        "message": "Documents deleted successfully",
    }
    mock_service.delete.assert_called_once()


def test_update_member_roles(test_client):
    client, mock_service = test_client
    updated = {**TEST_MEMBER_DATA[0], "roles": ["admin"]}
    mock_service.update_roles.return_value = updated

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        resp = client.http.patch(
            f"/members/{TEST_MEMBER_DATA[0]['id']}/roles",
            body=json.dumps({"roles": ["admin"]}),
            headers={
                "Authorization": "Bearer TOKEN",
                "Content-Type": "application/json",
            },
        )

    assert resp.status_code == 200
    assert resp.json_body == updated
    mock_service.update_roles.assert_called_once_with(
        user_id=TEST_MEMBER_DATA[0]["id"], roles=["admin"]
    )
