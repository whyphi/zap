from chalice import NotFoundError, Response, BadRequestError
from typing import Dict, List, Optional, Any, Union
from supabase import Client
from postgrest.exceptions import APIError
from chalicelib.modules.supabase_client import SupabaseClient


class BaseRepository:
    """
    Base repository class that provides common CRUD operations for Supabase tables.
    Specific repositories can inherit from this class to reuse common methods.
    """

    def __init__(self, table_name: str):
        self.client: Client = SupabaseClient().get_client()
        self.table_name = table_name

    def get_all(self, select_query: str = "*") -> List[Dict]:
        """Get all records from the table with optional field selection"""
        try:
            response = self.client.table(self.table_name).select(select_query).execute()
            return response.data
        except APIError as e:
            print(f"API Error fetching records from {self.table_name}: {str(e)}")
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return []
        except Exception as e:
            # Keep the general exception handler as a fallback
            print(f"Unexpected error fetching records from {self.table_name}: {str(e)}")
            return []

    def get_by_id(
        self, id_field: str, id_value: str, select_query: str = "*"
    ) -> Optional[Dict]:
        """Get a record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .select(select_query)
                .eq(id_field, id_value)
                .execute()
            )
            return response.data[0] if response.data else None
        except APIError as e:
            print(
                f"API Error fetching record by {id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return None
        except Exception as e:
            print(
                f"Unexpected error fetching record by {id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            return None

    def create(self, data: Dict):
        """Create a new record"""
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            return response.data[0] if response.data else None
        except APIError as e:
            print(
                f"API Error creating record in {self.table_name}: Error code: {e.code}, Message: {e.message}, Hint: {e.hint}"
            )
            raise BadRequestError(e.message)
        except Exception as e:
            print(f"Unexpected error creating record in {self.table_name}: {str(e)}")
            raise BadRequestError(
                f"Unexpected error creating record in {self.table_name}"
            )

    def update(self, id_field: str, id_value: str, data: Dict) -> Optional[Dict]:
        """Update an existing record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .update(data)
                .eq(id_field, id_value)
                .execute()
            )
            return response.data[0] if response.data else None
        except APIError as e:
            print(
                f"API Error updating record {id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return None
        except Exception as e:
            print(
                f"Unexpected error updating record {id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            return None

    def update_field(self, id_field: str, id_value: str, field: str, value: Any):
        """Update a single field in a record"""
        return self.update(id_field, id_value, {field: value})

    def delete(self, id_field: str, id_value: str):
        """Delete a record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .delete()
                .eq(id_field, id_value)
                .execute()
            )
            return bool(response.data)
        except APIError as e:
            print(
                f"API Error deleting record {id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return False
        except Exception as e:
            print(
                f"Unexpected error deleting record {id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            return False

    def toggle_boolean_field(
        self, id_field: str, id_value: str, field: str
    ) -> Optional[Dict]:
        """Toggle a boolean field in a record"""
        try:
            # First, get the current value
            record = self.get_by_id(id_field, id_value)
            if not record:
                return None

            # Toggle the value
            current_value = record.get(field, False)
            return self.update_field(id_field, id_value, field, not current_value)
        except APIError as e:
            print(
                f"API Error toggling field {field} for {id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return None
        except Exception as e:
            print(
                f"Unexpected error toggling field {field} for {id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            return None

    def query(self):
        """Return a query builder for more complex queries"""
        return self.client.table(self.table_name)
