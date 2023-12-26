from chalice.test import Client
from app import app
# from chalicelib.services.ListingService import listing_service

def test_index_route():
    with Client(app) as client:
        response = client.http.get('/')
        assert response.json_body == {'hello': 'world'}