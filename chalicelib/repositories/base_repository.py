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

    def __init__(self, table_name: str, id_field):
        self.client: Client = SupabaseClient().get_client()
        self.table_name = table_name
        self.id_field = id_field

    def get_all(self, select_query: str = "*"):
        """Get all records from the table with optional field selection"""
        try:
            response = self.client.table(self.table_name).select(select_query).execute()
            print("response", response.data)
            return response.data
        except APIError as e:
            print(f"API Error fetching records from {self.table_name}: {str(e)}")
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            raise BadRequestError(e.message)
        except Exception as e:
            # Keep the general exception handler as a fallback
            print(f"Unexpected error fetching records from {self.table_name}: {str(e)}")
            raise BadRequestError("Unexpected error fetching records.")

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
                raise NotFoundError("Error fetching record.")
            return response.data[0]
        except NotFoundError:
            raise  # Let NotFoundError ascend up without catching
        except APIError as e:
            print(
                f"API Error fetching record by {self.id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            raise BadRequestError(e.message)
        except Exception as e:
            print(
                f"Unexpected error fetching record by {self.id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            raise BadRequestError(f"Unexpected error fetching record.")

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
            raise BadRequestError(f"Unexpected error creating record")

    def update(self, id_value: str, data: Dict) -> Optional[Dict]:
        """Update an existing record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .update(data)
                .eq(self.id_field, id_value)
                .execute()
            )
            return response.data[0] if response.data else None
        except APIError as e:
            print(
                f"API Error updating record {self.id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return None
        except Exception as e:
            print(
                f"Unexpected error updating record {self.id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            return None

    def update_field(self, id_value: str, field: str, value: Any):
        """Update a single field in a record"""
        return self.update(self.id_field, id_value, {field: value})

    def delete(self, id_value: str):
        """Delete a record by its ID field"""
        try:
            response = (
                self.client.table(self.table_name)
                .delete()
                .eq(self.id_field, id_value)
                .execute()
            )
            return bool(response.data)
        except APIError as e:
            print(
                f"API Error deleting record {self.id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return False
        except Exception as e:
            print(
                f"Unexpected error deleting record {self.id_field}={id_value} from {self.table_name}: {str(e)}"
            )
            return False

    def toggle_boolean_field(self, id_value: str, field: str) -> Optional[Dict]:
        """Toggle a boolean field in a record"""
        try:
            # First, get the current value
            record = self.get_by_id(self.id_field, id_value)
            if not record:
                return None

            # Toggle the value
            current_value = record.get(field, False)
            return self.update_field(self.id_field, id_value, field, not current_value)
        except APIError as e:
            print(
                f"API Error toggling field {field} for {self.id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            print(f"Error code: {e.code}, Message: {e.message}, Hint: {e.hint}")
            return None
        except Exception as e:
            print(
                f"Unexpected error toggling field {field} for {self.id_field}={id_value} in {self.table_name}: {str(e)}"
            )
            return None

    def query(self):
        """Return a query builder for more complex queries"""
        return self.client.table(self.table_name)
