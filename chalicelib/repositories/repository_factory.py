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
    LISTINGS = RepositoryConfig(table_name="listings")
    APPLICATIONS = RepositoryConfig(table_name="applications")
    USERS = RepositoryConfig(table_name="users")
    EVENTS = RepositoryConfig(table_name="events")

    @staticmethod
    def create(config: RepositoryConfig) -> BaseRepository:
        """Create a repository instance with the given configuration"""
        return BaseRepository(table_name=config.table_name, id_field=config.id_field)

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
