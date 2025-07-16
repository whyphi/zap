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
    USER_ROLES = RepositoryConfig(table_name="user_roles", id_field="user_id")
    ROLES = RepositoryConfig(table_name="roles")
    
    EVENTS_MEMBER = RepositoryConfig(table_name="events_member")
    EVENT_TIMEFRAMES_MEMBER = RepositoryConfig(table_name="event_timeframes_member")
    EVENTS_MEMBER_ATTENDEES = RepositoryConfig(table_name="events_member_attendees")
    EVENT_TAGS = RepositoryConfig(table_name="event_tags", id_field="events_member_id")
    TAGS = RepositoryConfig(table_name="tags")

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
    def user_roles(cls) -> BaseRepository:
        return cls.create(cls.USER_ROLES)
    
    @classmethod
    def roles(cls) -> BaseRepository:
        return cls.create(cls.ROLES)

    @classmethod
    def events_member(cls) -> BaseRepository:
        return cls.create(cls.EVENTS_MEMBER)
    
    @classmethod
    def event_timeframes_member(cls) -> BaseRepository:
        return cls.create(cls.EVENT_TIMEFRAMES_MEMBER)   
    
    @classmethod
    def events_member_attendees(cls) -> BaseRepository:
        return cls.create(cls.EVENTS_MEMBER_ATTENDEES)
    
    @classmethod 
    def event_tags(cls) -> BaseRepository:
        return cls.create(cls.EVENT_TAGS)
    
    @classmethod
    def tags(cls) -> BaseRepository:
        return cls.create(cls.TAGS)


# Usage example:
# listings_repo = RepositoryFactory.listings()
# applications_repo = RepositoryFactory.applications()
