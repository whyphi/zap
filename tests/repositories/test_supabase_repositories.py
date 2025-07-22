import pytest
from unittest.mock import patch, MagicMock
from chalicelib.modules.supabase_client import SupabaseClient
from chalicelib.repositories.base_repository import BaseRepository
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import BadRequestError, NotFoundError
from postgrest.exceptions import APIError
from chalicelib.handlers.error_handler import GENERIC_CLIENT_ERROR


@pytest.fixture
def mock_supabase(monkeypatch):
    with patch(
        "chalicelib.modules.supabase_client.create_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        monkeypatch.setenv("ENV", "pytest-tests")
        monkeypatch.setenv("SUPABASE_URL", "http://fake.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "fake-key")
        yield mock_client


def test_supabase_client_initialization(mock_supabase):
    client = SupabaseClient()
    assert client.url == "http://fake.supabase.co"
    assert client.key == "fake-key"
    assert client.get_client() == mock_supabase


def test_repository_factory_creates_listings_repo(mock_supabase):
    repo = RepositoryFactory.listings()
    assert isinstance(repo, BaseRepository)
    assert repo.table_name == "listings"
    assert repo.id_fields == "id"


def test_base_repository_get_all_returns_all_records_from_table(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().select().execute.return_value.data = [
        {"id": 1, "name": "Alice"}
    ]

    result = repo.get_all()
    mock_supabase.table.assert_called_with("test_table")

    assert result == [{"id": 1, "name": "Alice"}]


def test_base_repository_get_all_raises_bad_request_error_on_api_error(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().select().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.get_all()

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)


def test_base_repository_get_by_id_returns_record_with_id_from_table(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().select().eq().execute.return_value.data = [{"id": "abc123"}]

    result = repo.get_by_id("abc123")
    mock_supabase.table().select().eq.assert_called_with("id", "abc123")

    assert result == {"id": "abc123"}


def test_base_repository_get_by_id_raises_not_found_error_on_empty_data(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().select().eq().execute.return_value.data = []

    with pytest.raises(NotFoundError) as exc_info:
        repo.get_by_id("123")

    assert "Test_table with ID '123' not found." in str(exc_info.value)


def test_base_repository_get_by_id_raises_bad_request_error_on_api_error(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().select().eq().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.get_by_id("abc123")

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)


def test_base_repository_get_all_by_field_returns_matching_records_from_table(
    mock_supabase,
):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().select().eq().execute.return_value.data = [
        {"test_field": "test_value"}
    ]

    result = repo.get_all_by_field("test_field", "test_value")
    mock_supabase.table().select().eq.assert_called_with("test_field", "test_value")

    assert result == [{"test_field": "test_value"}]


def test_base_repository_get_all_by_field_raises_bad_request_error_on_api_error(
    mock_supabase,
):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().select().eq().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.get_all_by_field("test_field", "test_value")

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)


def test_base_repository_create_returns_created_record_from_table(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().insert().execute.return_value.data = [{"id": "newid"}]

    result = repo.create({"foo": "bar"})
    mock_supabase.table().insert.assert_called_with({"foo": "bar"})

    assert result == [{"id": "newid"}]


def test_base_repository_create_raises_bad_request_error_on_api_error(
    mock_supabase,
):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().insert().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.create({"id": "test_id"})

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)


def test_base_repository_create_bulk_returns_created_records_from_table(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().insert().execute.return_value.data = [
        {"id": "newid1"},
        {"id": "newid2"},
        {"id": "newid3"},
    ]

    result = repo.create([{"foo": "bar1"}, {"foo": "bar2"}, {"foo": "bar3"}])
    mock_supabase.table().insert.assert_called_with(
        [{"foo": "bar1"}, {"foo": "bar2"}, {"foo": "bar3"}]
    )

    assert result == [
        {"id": "newid1"},
        {"id": "newid2"},
        {"id": "newid3"},
    ]


def test_base_repository_create_bulk_raises_bad_request_error_on_api_error(
    mock_supabase,
):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().insert().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.create([{"foo": "bar1"}, {"foo": "bar2"}, {"foo": "bar3"}])

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)


def test_base_repository_update_returns_updated_record_from_table(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().update().eq().execute.return_value.data = [
        {"id": "123", "updated": True}
    ]

    result = repo.update("123", {"updated": True})
    mock_supabase.table().update.assert_called_with({"updated": True})
    mock_supabase.table().update().eq.assert_called_with("id", "123")

    assert result == {"id": "123", "updated": True}


def test_base_repository_update_raises_not_found_error_on_empty_data(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().update().eq().execute.return_value.data = []

    with pytest.raises(NotFoundError) as exc_info:
        repo.update("123", {"id": "123"})

    assert "Test_table with ID '123' not found." in str(exc_info.value)


def test_base_repository_update_raises_bad_request_error_on_api_error(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().update().eq().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.update("123", {"id": "123"})

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)


def test_base_repository_toggle_boolean_field_returns_updated_record_from_table(
    mock_supabase,
):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    # Simulate get_by_id
    mock_supabase.table().select().eq().execute.return_value.data = [
        {"id": "1", "is_active": False}
    ]
    # Simulate update_field
    mock_supabase.table().update().eq().execute.return_value.data = [
        {"id": "1", "is_active": True}
    ]

    result = repo.toggle_boolean_field("1", "is_active")

    assert result == {"id": "1", "is_active": True}


def test_base_repository_toggle_boolean_field_raises_bad_request_error_on_api_error(
    mock_supabase,
):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().select().eq().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.toggle_boolean_field("123", "test_field")

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)


def test_base_repository_delete__returns_deleted_record_from_table(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase
    mock_supabase.table().delete().eq().execute.return_value.data = [{"id": "1"}]

    result = repo.delete("1")
    mock_supabase.table().delete.assert_called_with()
    mock_supabase.table().delete().eq.assert_called_with("id", "1")

    assert result == [{"id": "1"}]


def test_base_repository_delete_raises_not_found_error_on_empty_data(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().delete().eq().execute.return_value.data = []

    with pytest.raises(NotFoundError) as exc_info:
        repo.delete("123")

    assert "Test_table with ID '123' not found." in str(exc_info.value)


def test_base_repository_delete_raises_bad_request_error_on_api_error(mock_supabase):
    repo = BaseRepository("test_table", "id")
    repo.client = mock_supabase

    mock_supabase.table().delete().eq().execute.side_effect = APIError(
        error={"message": "API failed"}
    )

    with pytest.raises(BadRequestError) as exc_info:
        repo.delete("abc123")

    assert GENERIC_CLIENT_ERROR in str(exc_info.value)
