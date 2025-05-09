from chalicelib.modules.supabase_client import SupabaseClient

TABLE_NAME = "listings"


class ListingsRepository:
    def __init__(self):
        self.client = SupabaseClient().get_client()

    def get_all_listings(self):
        try:
            response = self.client.table(TABLE_NAME).select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching listings: {str(e)}")
            return []

    def get_listing_by_id(self, listing_id: str):
        try:
            response = (
                self.client.table(TABLE_NAME)
                .select("*")
                .eq("listingId", listing_id)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching listing by id {listing_id}: {str(e)}")
            return None

    def create_listing(self, data: dict):
        try:
            response = self.client.table(TABLE_NAME).insert(data).execute()
            return response.data
        except Exception as e:
            print(f"Error creating listing: {str(e)}")
            return None


listings_repo = ListingsRepository()


# # File: chalicelib/services/listing_service.py
# from chalicelib.modules.listings_repository import ListingsRepository

# class ListingService:
#     def __init__(self):
#         self.listings_repo = ListingsRepository()

#     def get_all(self):
#         return self.listings_repo.get_all_listings()

#     def get(self, id: str):
#         return self.listings_repo.get_listing_by_id(id)

#     def create(self, data: dict):
#         return self.listings_repo.create_listing(data)

# listing_service = ListingService()
