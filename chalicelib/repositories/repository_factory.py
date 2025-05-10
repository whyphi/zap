from typing import Dict, Any
from dataclasses import dataclass
from chalicelib.repositories.base_repository import BaseRepository


@dataclass
class RepositoryConfig:
    """Configuration for a repository"""
    table_name: str
    id_field: str = "id"


class RepositoryFactory:
    """Factory for creating repository instances with predefined configurations"""
    
    # Repository configuration constants
    LISTINGS = RepositoryConfig(table_name="listings", id_field="listing_id")
    APPLICATIONS = RepositoryConfig(table_name="applications", id_field="applicant_id")
    USERS = RepositoryConfig(table_name="users", id_field="user_id")
    EVENTS = RepositoryConfig(table_name="events", id_field="event_id")
    
    @staticmethod
    def create(config: RepositoryConfig) -> BaseRepository:
        """Create a repository instance with the given configuration"""
        return BaseRepository(table_name=config.table_name)
    
    @classmethod
    def listings(cls) -> BaseRepository:
        return cls.create(cls.LISTINGS)
    
    @classmethod
    def applications(cls) -> BaseRepository:
        return cls.create(cls.APPLICATIONS)
    
    @classmethod
    def users(cls) -> BaseRepository:
        return cls.create(cls.USERS)
    
    @classmethod
    def events(cls) -> BaseRepository:
        return cls.create(cls.EVENTS)


# Usage example:
# listings_repo = RepositoryFactory.listings()
# applications_repo = RepositoryFactory.applications()