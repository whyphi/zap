from chalice.app import Blueprint
from chalicelib.services.ListingService import ListingService
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalicelib.handlers.error_handler import handle_exceptions
from chalicelib.decorators import auth
from chalicelib.models.roles import Roles


listings_api = Blueprint(__name__)

def register_routes(listing_service: ListingService):
    @listings_api.route("/listings/create", methods=["POST"], cors=True)
    @auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
    @handle_exceptions
    def create_listing():
        """Creates a new listing with given information"""
        data: dict = listings_api.current_request.json_body
        include_events_attended = data.pop("include_events_attended")
        return listing_service.create(data, include_events_attended)


    @listings_api.route("/apply", methods=["POST"], cors=True)
    @handle_exceptions
    def apply_to_listing():
        return listing_service.apply(listings_api.current_request.json_body)


    @listings_api.route("/listings/{id}", methods=["GET"], cors=True)
    @handle_exceptions
    def get_listing(id):
        """Gets a listing from id"""
        return listing_service.get(id)


    @listings_api.route("/listings", methods=["GET"], cors=True)
    @auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
    @handle_exceptions
    def get_all_listings():
        """Gets all listings available"""
        return listing_service.get_all()


    @listings_api.route("/listings/{id}", methods=["DELETE"], cors=True)
    @auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
    @handle_exceptions
    def delete_listing(id):
        """Deletes a listing with the given ID."""
        return listing_service.delete(id)


    @listings_api.route("/listings/{id}/toggle/visibility", methods=["PATCH"], cors=True)
    @auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
    @handle_exceptions
    def toggle_visibility(id):
        """Toggles visibilility of a given <listing_id>"""
        return listing_service.toggle_visibility(id)


    @listings_api.route("/listings/{id}/toggle/encryption", methods=["PATCH"], cors=True)
    @auth(listings_api, roles=[Roles.ADMIN])
    @handle_exceptions
    def toggle_encryption(id):
        """Encrypts a listing with the given ID."""
        return listing_service.toggle_encryption(id)


    @listings_api.route("/listings/{id}/update-field", methods=["PATCH"], cors=True)
    @auth(listings_api, roles=[Roles.ADMIN, Roles.MEMBER])
    @handle_exceptions
    def update_listing_field_route(id):
        return listing_service.update_field_route(
            id, listings_api.current_request.json_body
        )
