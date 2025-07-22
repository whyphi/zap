from typing import List
from dataclasses import dataclass, field
from chalicelib.repositories.base_repository import BaseRepository


@dataclass
class RepositoryConfig:
    """Configuration for a repository"""

    table_name: str
    id_fields: List[str] = field(default_factory=lambda: ["id"])


class RepositoryFactory:
    """Factory for creating repository instances with predefined configurations"""

    # Repository configuration constants
    LISTINGS = RepositoryConfig(table_name="listings")
    APPLICATIONS = RepositoryConfig(table_name="applications")

    USERS = RepositoryConfig(table_name="users")
    USER_ROLES = RepositoryConfig(
        table_name="user_roles", id_fields=["user_id", "role_id"]
    )
    ROLES = RepositoryConfig(table_name="roles")

    EVENTS_MEMBER = RepositoryConfig(table_name="events_member")
    EVENT_TIMEFRAMES_MEMBER = RepositoryConfig(table_name="event_timeframes_member")
    EVENTS_MEMBER_ATTENDEES = RepositoryConfig(table_name="events_member_attendees")
    EVENT_TAGS = RepositoryConfig(
        table_name="event_tags", id_fields=["events_member_id", "tag_id"]
    )
    TAGS = RepositoryConfig(table_name="tags")

    EVENT_TIMEFRAMES_RUSH = RepositoryConfig(table_name="event_timeframes_rush")
    EVENTS_RUSH = RepositoryConfig(table_name="events_rush")
    EVENTS_RUSH_ATTENDEES = RepositoryConfig(
        table_name="events_rush_attendees", id_fields=["event_id", "rushee_id"]
    )

    @staticmethod
    def create(config: RepositoryConfig) -> BaseRepository:
        """Create a repository instance with the given configuration"""
        return BaseRepository(table_name=config.table_name, id_fields=config.id_fields)

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

    @classmethod
    def rush_categories(cls):
        return cls.create(cls.EVENT_TIMEFRAMES_RUSH)

    @classmethod
    def rush_events(cls):
        return cls.create(cls.EVENTS_RUSH)

    @classmethod
    def rush_attendees(cls):
        return cls.create(cls.EVENTS_RUSH_ATTENDEES)


# Usage example:
# listings_repo = RepositoryFactory.listings()
# applications_repo = RepositoryFactory.applications()
