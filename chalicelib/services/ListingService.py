from chalice.app import BadRequestError
from pydantic import ValidationError
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalicelib.services.EventsRushService import events_rush_service
from chalicelib.utils import CaseConverter, JSONType
from chalicelib.handlers.error_handler import GENERIC_CLIENT_ERROR
import uuid
import logging

logger = logging.getLogger(__name__)

# TODO: DON'T FORGET TO DECIDE WHAT TO DO WITH ListingService.create (temporarily create MongoDB event???)


class ListingService:
    def __init__(self):
        self.listings_repo = RepositoryFactory.listings()

    # TODO: prevent duplicate names... (also for rush-category)
    def create(self, data: JSONType):
        data = CaseConverter.convert_keys(
            data=data, convert_func=CaseConverter.to_snake_case
        )
        if not isinstance(data, dict):
            logger.error(f"[ApplicantService.apply] Invalid inputs: {data}")
            raise ValidationError(GENERIC_CLIENT_ERROR)

        id = str(uuid.uuid4())
        data["id"] = id
        data["is_visible"] = True
        data["is_encrypted"] = False

        # TODO: check for dup name BEFORE going to rush-category creation
        # if includeEventsAttended, create corresponding rush category (and create foreign-key)
        # if data.get("includeEventsAttended", None):
        #     events_rush_data = {"name": data["title"], "defaultRushCategory": False}
        #     rush_category_id = events_rush_service.create_rush_category(
        #         data=events_rush_data
        #     )
        #     data["rushCategoryId"] = str(rush_category_id)

        self.listings_repo.create(data=data)

        return {"msg": True}

    def get(self, id: str):
        data = self.listings_repo.get_by_id(id_value=id)
        return CaseConverter.convert_keys(
            data=data, convert_func=CaseConverter.to_camel_case
        )

    def get_all(self):
        data = self.listings_repo.get_all()
        # TODO: fix type conversion... may need to decrease strictness in CaseConverter
        return CaseConverter.convert_keys(
            data=data, convert_func=CaseConverter.to_camel_case
        )

    # TODO: also delete corresponding rush-category
    def delete(self, id: str):
        self.listings_repo.delete(id_value=id)
        return {"msg": True}

    def toggle_visibility(self, id: str):
        self.listings_repo.toggle_boolean_field(id_value=id, field="is_visible")
        return {"msg": True}

    def toggle_encryption(self, id: str):
        self.listings_repo.toggle_boolean_field(id_value=id, field="is_encrypted")
        return {"msg": True}

    def update_field_route(self, id: str, data: dict):
        # Get field and value from object
        field = data.get("field", None)
        value = data.get("value", None)

        if not (field and value):
            logger.error(f"[ListingService.update_field_route] Invalid inputs: {data}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

        self.listings_repo.update_field(id_value=id, field=field, value=value)
        return {"msg": True}


listing_service = ListingService()
