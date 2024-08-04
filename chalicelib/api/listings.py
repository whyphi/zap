from chalice import Blueprint
from chalicelib.services.ListingService import listing_service
from chalicelib.handlers.error_handler import handle_exceptions
from chalicelib.decorators import auth
from chalicelib.models.roles import Roles


listings_api = Blueprint(__name__)


# TODO: Change /submit to /apply
@listings_api.route("/submit", methods=["POST"], cors=True)
def apply_to_listing():
    return listing_service.apply(listings_api.current_request.json_body)


@listings_api.route("/create", methods=["POST"], cors=True)
@auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
def create_listing():
    """Creates a new listing with given information"""
    return listing_service.create(listings_api.current_request.json_body)


@listings_api.route("/listings/{id}", methods=["GET"], cors=True)
def get_listing(id):
    """Gets a listing from id"""
    return listing_service.get(id)


@listings_api.route("/listings", methods=["GET"], cors=True)
@auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
def get_all_listings():
    """Gets all listings available"""
    return listing_service.get_all()


@listings_api.route("/listings/{id}", methods=["DELETE"], cors=True)
@auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
def delete_listing(id):
    """Deletes a listing with the given ID."""
    try:
        return listing_service.delete(id)
    except Exception as e:
        listings_api.log.debug(e)


@listings_api.route("/listings/{id}/toggle/visibility", methods=["PATCH"], cors=True)
@auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
def toggle_visibility(id):
    """Toggles visibilility of a given <listing_id>"""
    try:
        return listing_service.toggle_visibility(id)
    except Exception as e:
        listings_api.log.debug(e)


@listings_api.route("/listings/{id}/update-field", methods=["PATCH"], cors=True)
@auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
@handle_exceptions
def update_listing_field_route(id):
    try:
        return listing_service.update_field_route(
            id, listings_api.current_request.json_body
        )
    except Exception as e:
        listings_api.log.debug(e)
