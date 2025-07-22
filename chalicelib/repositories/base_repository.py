from chalice.app import NotFoundError, Response, BadRequestError
from typing import Dict, List, Optional, Any, Union
from supabase import Client
from postgrest.exceptions import APIError
from chalicelib.modules.supabase_client import SupabaseClient
from chalicelib.handlers.error_handler import GENERIC_CLIENT_ERROR
import logging
import os

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Base repository class that provides common CRUD operations for Supabase tables.
    Specific repositories can inherit from this class to reuse common methods.
    """

    def __init__(self, table_name: str, id_field):
        ENV = os.getenv("ENV")
        if ENV == "pytest-init":
            return
        self.client: Client = SupabaseClient().get_client()
        self.table_name = table_name
        self.id_field = id_field

    ########## CREATE ##########

    def create(self, data: Union[Dict, List]):
        """Create a new record"""
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            return response.data
        except APIError as e:
            logger.error(f"[BaseRepository.create] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    ########## READ ##########

    def get_all(self, select_query: str = "*"):
        """Get all records from the table with optional field selection"""
        try:
            response = self.client.table(self.table_name).select(select_query).execute()
            return response.data
        except APIError as e:
            logger.error(f"[BaseRepository.get_all] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    def get_by_id(self, id_value: str, select_query: str = "*") -> Dict:
        """Get a record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .select(select_query)
                .eq(self.id_field, id_value)
                .execute()
            )

            if not response.data:
                error_message = (
                    f"{self.table_name.capitalize()} with ID '{id_value}' not found."
                )
                raise NotFoundError(error_message)
            return response.data[0]
        except APIError as e:
            logger.error(f"[BaseRepository.get_by_id] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    def get_by_ids(self, id_fields: Dict[str, Any], select_query: str = "*") -> Dict:
        """Get a record by matching all provided id_fields"""
        try:
            query = self.client.table(self.table_name).select(select_query)
            for field, value in id_fields.items():
                query = query.eq(field, value)
            response = query.execute()

            if not response.data:
                error_message = (
                    f"{self.table_name.capitalize()} with keys {id_fields} not found."
                )
                raise NotFoundError(error_message)

            return response.data[0]
        except APIError as e:
            logger.error(f"[BaseRepository.get_by_ids] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    def get_all_by_field(
        self, field: str, value: Any, select_query: str = "*"
    ) -> List[Dict]:
        """Get all records where a specific field matches a value"""
        try:
            response = (
                self.client.table(self.table_name)
                .select(select_query)
                .eq(field, value)
                .execute()
            )
            return response.data
        except APIError as e:
            logger.error(f"[BaseRepository.get_by_field] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    def get_nested(self, nested_table: str):
        """
        Performs a select with a nested foreign table using PostgREST syntax. For example,
        we can get all events_rush associated with a timeframe by calling
        `self.event_timeframes_rush.get_nested(nested_table=events_rush)`.

        Args:
            nested (str): The nested table name.

        Returns:
            List[Dict]: List of rows with nested related table data.
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select(f"*, {nested_table}(*)")
                .execute()
            )
            return response.data
        except APIError as e:
            logger.error(f"[BaseRepository.get_nested] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    ########### UPDATE ###########

    def update(self, id_value: str, data: Dict) -> Optional[Dict]:
        """Update an existing record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .update(data)
                .eq(self.id_field, id_value)
                .execute()
            )
            if not response.data:
                error_message = (
                    f"{self.table_name.capitalize()} with ID '{id_value}' not found."
                )
                raise NotFoundError(error_message)
            return response.data[0]
        except APIError as e:
            logger.error(f"[BaseRepository.update] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    def update_field(self, id_value: str, field: str, value: Any):
        """Update a single field in a record"""
        return self.update(id_value, {field: value})

    ########## DELETE ##########

    def delete(self, id_value: str) -> List:
        """Delete a record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .delete()
                .eq(self.id_field, id_value)
                .execute()
            )

            if not response.data:
                error_message = (
                    f"{self.table_name.capitalize()} with ID '{id_value}' not found."
                )
                raise NotFoundError(error_message)
            return response.data

        except APIError as e:
            logger.error(f"[BaseRepository.delete] Supabase error: {e.message}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    ########## MISC ##########

    def toggle_boolean_field(self, id_value: str, field: str) -> Optional[Dict]:
        """Toggle a boolean field in a record"""
        try:
            record = self.get_by_id(id_value)

            current_value = record.get(field, False)
            return self.update_field(id_value, field, not current_value)
        except APIError as e:
            logger.error(
                f"[BaseRepository.toggle_boolean_field] Supabase error: {e.message}"
            )
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    # TODO: maybe implement this (as needed)
    def query(self):
        """Return a query builder for more complex queries"""
        return self.client.table(self.table_name)
