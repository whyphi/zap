import pytest
from unittest.mock import patch, MagicMock
from chalicelib.modules.supabase_client import SupabaseClient
from chalicelib.repositories.base_repository import BaseRepository
from chalicelib.repositories.repository_factory import RepositoryFactory


@pytest.fixture
def mock_supabase(monkeypatch):
    with patch(
        "chalicelib.modules.supabase_client.create_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        monkeypatch.setenv("ENV", "local")
        monkeypatch.setenv("SUPABASE_URL", "http://fake.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "fake-key")
        yield mock_client


# =====================================================
# Supabase initialization tests
# =====================================================


def test_supabase_client_initialization(mock_supabase):
    client = SupabaseClient()
    assert client.url == "http://fake.supabase.co"
    assert client.key == "fake-key"
    assert client.get_client() == mock_supabase


# =====================================================
# Repository factory tests
# =====================================================


def test_repository_factory_creates_listings_repo(mock_supabase):
    repo = RepositoryFactory.listings()
    assert isinstance(repo, BaseRepository)
    assert repo.table_name == "listings"
    assert repo.id_field == "id"


# =====================================================
# Base repository tests
# =====================================================


def test_base_repository_get_all(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().select().execute.return_value.data = [
        {"id": 1, "name": "Alice"}
    ]

    result = repo.get_all()
    mock_supabase.table.assert_called_with("test_table")

    assert result == [{"id": 1, "name": "Alice"}]


def test_base_repository_get_by_id(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().select().eq().execute.return_value.data = [{"id": "abc123"}]

    result = repo.get_by_id("abc123")
    mock_supabase.table().select().eq.assert_called_with("id", "abc123")

    assert result == {"id": "abc123"}


def test_base_repository_create(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().insert().execute.return_value.data = [{"id": "newid"}]

    result = repo.create({"foo": "bar"})
    mock_supabase.table().insert.assert_called_with({"foo": "bar"})

    assert result == {"id": "newid"}


def test_base_repository_update(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().update().eq().execute.return_value.data = [
        {"id": "123", "updated": True}
    ]

    result = repo.update("123", {"updated": True})
    mock_supabase.table().update.assert_called_with({"updated": True})
    mock_supabase.table().update().eq.assert_called_with("id", "123")

    assert result is not None
    assert result["updated"] is True


# def test_base_repository_toggle_boolean_field(mock_supabase):
#     repo = BaseRepository("test_table", "id")
#     repo.client = mock_supabase

#     # Simulate get_by_id
#     mock_supabase.table().select().eq().execute.return_value.data = [{"id": "1", "is_active": False}]
#     # Simulate update_field
#     mock_supabase.table().update().eq().execute.return_value.data = [{"id": "1", "is_active": True}]

#     result = repo.toggle_boolean_field("1", "is_active")
#     assert result["is_active"] is True


# def test_base_repository_delete(mock_supabase):
#     repo = BaseRepository("test_table", "id")
#     repo.client = mock_supabase
#     mock_supabase.table().delete().eq().execute.return_value.data = [{"id": "1"}]

#     result = repo.delete("1")
#     assert result is True
