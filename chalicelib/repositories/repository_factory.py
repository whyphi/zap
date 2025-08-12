from typing import Optional
from dataclasses import dataclass
from chalicelib.repositories.base_repository import BaseRepository
from supabase import Client


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

    RUSHEES = RepositoryConfig(table_name="rushees")

    EVENT_TIMEFRAMES_RUSH = RepositoryConfig(table_name="event_timeframes_rush")
    EVENTS_RUSH = RepositoryConfig(table_name="events_rush")
    EVENTS_RUSH_ATTENDEES = RepositoryConfig(table_name="events_rush_attendees")

    @staticmethod
    def create(
        config: RepositoryConfig, client: Optional[Client] = None
    ) -> BaseRepository:
        """Create a repository instance with the given configuration"""
        return BaseRepository(
            table_name=config.table_name, id_field=config.id_field, client=client
        )

    @classmethod
    def listings(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.LISTINGS, client)

    @classmethod
    def applications(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.APPLICATIONS, client=client)

    @classmethod
    def users(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.USERS, client=client)

    @classmethod
    def user_roles(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.USER_ROLES, client=client)

    @classmethod
    def roles(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.ROLES, client=client)

    @classmethod
    def events_member(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.EVENTS_MEMBER, client=client)

    @classmethod
    def event_timeframes_member(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.EVENT_TIMEFRAMES_MEMBER, client=client)

    @classmethod
    def events_member_attendees(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.EVENTS_MEMBER_ATTENDEES, client=client)

    @classmethod
    def event_tags(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.EVENT_TAGS, client=client)

    @classmethod
    def tags(cls, client: Optional[Client] = None) -> BaseRepository:
        return cls.create(cls.TAGS, client=client)

    @classmethod
    def event_timeframes_rush(cls, client: Optional[Client] = None):
        return cls.create(cls.EVENT_TIMEFRAMES_RUSH, client=client)

    @classmethod
    def events_rush(cls, client: Optional[Client] = None):
        return cls.create(cls.EVENTS_RUSH, client=client)

    @classmethod
    def events_rush_attendees(cls, client: Optional[Client] = None):
        return cls.create(cls.EVENTS_RUSH_ATTENDEES, client=client)

    @classmethod
    def rushees(cls, client: Optional[Client] = None):
        return cls.create(cls.RUSHEES, client=client)


# Usage example:
# listings_repo = RepositoryFactory.listings()
# applications_repo = RepositoryFactory.applications()
