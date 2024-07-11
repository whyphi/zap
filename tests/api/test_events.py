from chalice.test import Client
from unittest.mock import patch
import json

from app import app

with open("tests/fixtures/events/general/sample_timeframes.json") as f:
    SAMPLE_TIMEFRAMES = json.load(f)

with open("tests/fixtures/events/general/sample_timeframe_sheets.json") as f:
    SAMPLE_TIMEFRAME_SHEETS = json.load(f)

def test_create_timeframe():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventService.event_service.create_timeframe"
            ) as mock_create_timeframe:
                mock_create_timeframe.return_value = {"msg": True}
                response = client.http.post(
                    f"/timeframes",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}


def test_get_all_timeframes():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventService.event_service.get_all_timeframes",
            ) as mock_get_all_timeframes:
                mock_get_all_timeframes.return_value = SAMPLE_TIMEFRAMES
                response = client.http.get(
                    f"/timeframes",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == SAMPLE_TIMEFRAMES

def test_get_timeframe():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventService.event_service.get_timeframe",
            ) as mock_get_timeframe:
                mock_get_timeframe.return_value = SAMPLE_TIMEFRAMES[0]
                response = client.http.get(
                    f"/timeframes/test_timeframe_id",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == SAMPLE_TIMEFRAMES[0]

# TODO: fix bug with delete_timeframe (getting `500 internal service error`)
# def test_delete_timeframe():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.EventService.event_service.get_timeframe",
#             ) as mock_delete:
#                 mock_delete.return_value = {"status": True}
#                 response = client.http.delete(
#                     f"/timeframes/{SAMPLE_TIMEFRAMES[0]['_id']}",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 assert response.status_code == 200
#                 # assert response.json_body == None


def test_create_event():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventService.event_service.create_event"
            ) as mock_create_event:
                mock_create_event.return_value = {"msg": True}
                response = client.http.post(
                    f"/timeframes/{SAMPLE_TIMEFRAMES[0]['_id']}/events",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}

def test_get_event():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventService.event_service.get_timeframe",
            ) as mock_get_timeframe:
                mock_get_timeframe.return_value = SAMPLE_TIMEFRAMES[0]
                response = client.http.get(
                    f"/timeframes/test_timeframe_id",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == SAMPLE_TIMEFRAMES[0]

def test_get_timeframe_sheets():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventService.event_service.get_timeframe_sheets",
            ) as mock_get_timeframe_sheets:
                mock_get_timeframe_sheets.return_value = SAMPLE_TIMEFRAME_SHEETS
                response = client.http.get(
                    f"/timeframes/test_timeframe_id/sheets",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == SAMPLE_TIMEFRAME_SHEETS

# def get_timeframe_sheets(timeframe_id: str):

# def checkin(event_id: str):

# def delete_event(event_id: str):

# def get_rush_events():

# def get_rush_event(event_id):

# def create_rush_category():

# def create_rush_event():

# def modify_rush_event():

# def modify_rush_settings():

# def checkin_rush(event_id):

# def delete_rush_event(event_id):


# def test_get_all_listings():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.ListingService.listing_service.get_all"
#             ) as mock_get_all:
#                 mock_get_all.return_value = TEST_LISTINGS
#                 response = client.http.get(
#                     f"/listings",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 assert response.status_code == 200
#                 assert response.json_body == TEST_LISTINGS


# def test_delete_listing():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.ListingService.listing_service.delete"
#             ) as mock_delete:
#                 mock_delete.return_value = {"status": True}
#                 response = client.http.delete(
#                     f"/listings/{TEST_LISTINGS[0]['listingId']}",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 assert response.status_code == 200
#                 assert response.json_body == {"status": True}


# def test_toggle_visibility():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.ListingService.listing_service.toggle_visibility"
#             ) as mock_toggle_visibility:
#                 mock_toggle_visibility.return_value = {"status": True}
#                 response = client.http.patch(
#                     f"/listings/{TEST_LISTINGS[0]['listingId']}/toggle/visibility",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 assert response.status_code == 200
#                 assert response.json_body == {"status": True}


# def test_update_listing_field_route():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.ListingService.listing_service.update_field_route"
#             ) as mock_update_field_route:
#                 mock_update_field_route.return_value = {
#                     "status": True,
#                     "updated_listing": TEST_LISTINGS[1],
#                 }
#                 response = client.http.patch(
#                     f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 print(response.json_body)

#                 assert response.status_code == 200
#                 assert response.json_body == {
#                     "status": True,
#                     "updated_listing": TEST_LISTINGS[1],
#                 }


# def test_update_listing_field_route_not_found():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.ListingService.listing_service.update_field_route"
#             ) as mock_update_field_route:
#                 mock_update_field_route.side_effect = NotFoundError("Not found")

#                 response = client.http.patch(
#                     f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 assert response.json_body == None


# def test_update_listing_field_route_bad_request():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.ListingService.listing_service.update_field_route"
#             ) as mock_update_field_route:
#                 mock_update_field_route.side_effect = BadRequestError("Bad request")

#                 response = client.http.patch(
#                     f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 # body, status_code = response.json_body

#                 assert response.json_body == None


# def test_update_listing_field_route_exception():
#     with Client(app) as client:
#         with patch("chalicelib.decorators.jwt.decode") as mock_decode:
#             # Assuming the decoded token has the required role
#             mock_decode.return_value = {"role": "admin"}
#             with patch(
#                 "chalicelib.services.ListingService.listing_service.update_field_route"
#             ) as mock_update_field_route:
#                 mock_update_field_route.side_effect = Exception("Error")

#                 response = client.http.patch(
#                     f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field",
#                     headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
#                 )

#                 assert response.json_body == None
