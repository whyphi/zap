from chalice import Blueprint
from chalicelib.services.ListingService import listing_service
from chalicelib.handlers.error_handler import handle_exceptions
from pydantic import ValidationError

listings_api = Blueprint(__name__)


# TODO: Change /submit to /apply
@listings_api.route("/submit", methods=["POST"], cors=True)
def apply_to_listing():
    return listing_service.apply(listings_api.current_request.json_body)


@listings_api.route("/create", methods=["POST"], cors=True)
def create_listing():
    """Creates a new listing with given information"""
    return listing_service.create(listings_api.current_request.json_body)


@listings_api.route("/listings/{id}", methods=["GET"], cors=True)
def get_listing(id):
    """Gets a listing from id"""
    return listing_service.get(id)


@listings_api.route("/listings", methods=["GET"], cors=True)
def get_all_listings():
    """Gets all listings available"""
    return listing_service.get_all()


@listings_api.route("/listings/{id}", methods=["DELETE"], cors=True)
def delete_listing(id):
    """Deletes a listing with the given ID."""
    return listing_service.delete(id)


@listings_api.route("/listings/{id}/toggle/visibility", methods=["PATCH"], cors=True)
def toggle_visibility(id):
    """Toggles visibilility of a given <listing_id>"""
    return listing_service.toggle_visibility(id)


@listings_api.route("/listings/{id}/update-field", methods=["PATCH"], cors=True)
@handle_exceptions
def update_listing_field_route(id):
    return listing_service.update_field_route(id, listings_api.current_request.json_body)