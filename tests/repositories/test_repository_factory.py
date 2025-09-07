import pytest
from unittest.mock import MagicMock
from chalicelib.repositories.repository_factory import (
    RepositoryFactory,
    RepositoryConfig,
)
from chalicelib.repositories.base_repository import BaseRepository


@pytest.fixture
def mock_client():
    return MagicMock()


def test_repository_factory_creates_all_repos_with_default_id_field(mock_client):
    # These should use default id_field 'id'
    repo_classes = [
        RepositoryFactory.listings,
        RepositoryFactory.applications,
        RepositoryFactory.users,
        RepositoryFactory.roles,
        RepositoryFactory.events_member,
        RepositoryFactory.event_timeframes_member,
        RepositoryFactory.events_member_attendees,
        RepositoryFactory.tags,
        RepositoryFactory.event_timeframes_rush,
        RepositoryFactory.events_rush,
        RepositoryFactory.events_rush_attendees,
        RepositoryFactory.rushees,
    ]
    for repo_class in repo_classes:
        repo = repo_class(client=mock_client)
        assert isinstance(repo, BaseRepository)
        assert repo.client == mock_client
        assert repo.id_field == "id"


def test_repository_factory_creates_repos_with_custom_id_field(mock_client):
    # These have custom id_field
    repo = RepositoryFactory.user_roles(client=mock_client)
    assert repo.id_field == "user_id"
    repo = RepositoryFactory.event_tags(client=mock_client)
    assert repo.id_field == "events_member_id"


def test_repository_factory_create_method_accepts_config_and_client(mock_client):
    config = RepositoryConfig(table_name="custom_table", id_field="custom_id")
    repo = RepositoryFactory.create(config, client=mock_client)
    assert isinstance(repo, BaseRepository)
    assert repo.table_name == "custom_table"
    assert repo.id_field == "custom_id"
    assert repo.client == mock_client


def test_repository_factory_default_client(monkeypatch):
    # If no client is passed, BaseRepository should use SupabaseClient.get_client()
    # We'll patch SupabaseClient.get_client to return a dummy client
    from chalicelib.modules import supabase_client

    dummy_client = object()
    monkeypatch.setattr(
        supabase_client.SupabaseClient, "get_client", staticmethod(lambda: dummy_client)
    )
    repo = RepositoryFactory.listings()
    assert repo.client == dummy_client
