import pytest
from unittest.mock import Mock, patch
from chalicelib.services.EventsMemberService import EventsMemberService
import datetime
import json

with open("tests/fixtures/events/general/sample_timeframes.json") as f:
    SAMPLE_TIMEFRAMES: list = json.load(f)

with open("tests/fixtures/events/general/sample_timeframe_sheets.json") as f:
    SAMPLE_TIMEFRAME_SHEETS: list = json.load(f)


@pytest.fixture
def service():
    mock_events_member_repo = Mock()
    mock_event_timeframes_member_repo = Mock()
    mock_events_member_attendees_repo = Mock()
    mock_event_tags_repo = Mock()
    mock_tags_repo = Mock()
    mock_users_repo = Mock()

    with patch(
        "chalicelib.modules.google_sheets.GoogleSheetsModule"
    ) as MockGoogleSheetsModule, patch("chalicelib.modules.ses.ses") as mock_ses:
        service = EventsMemberService(
            events_member_repo=mock_events_member_repo,
            event_timeframes_member_repo=mock_event_timeframes_member_repo,
            events_member_attendees_repo=mock_events_member_attendees_repo,
            event_tags_repo=mock_event_tags_repo,
            tags_repo=mock_tags_repo,
            users_repo=mock_users_repo,
        )
        yield (
            service,
            mock_events_member_repo,
            mock_event_timeframes_member_repo,
            mock_events_member_attendees_repo,
            mock_event_tags_repo,
            mock_tags_repo,
            mock_users_repo,
            MockGoogleSheetsModule,
            mock_ses,
        )


def test_create_timeframe(service):
    service_inst, _, mock_event_timeframes_member_repo, *_ = service
    timeframe_data = {
        "name": "testTimeframeName",
        "spreadsheet_id": "testSpreadsheetId",
    }
    fixed_uuid = "12345678123456781234567812345678"
    with patch("uuid.uuid4", return_value=fixed_uuid):
        mock_event_timeframes_member_repo.create.return_value = {
            "id": fixed_uuid,
            **timeframe_data,
        }
        result = service_inst.create_timeframe(timeframe_data)
        mock_event_timeframes_member_repo.create.assert_called_once_with(timeframe_data)
        assert result == {"id": fixed_uuid, **timeframe_data}


def test_get_timeframe(service):
    service_inst, _, mock_event_timeframes_member_repo, *_ = service
    mock_event_timeframes_member_repo.get_by_id.return_value = SAMPLE_TIMEFRAMES[0]
    timeframe_id = SAMPLE_TIMEFRAMES[0]["id"]
    result = service_inst.get_timeframe(timeframe_id)
    mock_event_timeframes_member_repo.get_by_id.assert_called_once_with(timeframe_id)
    assert result == SAMPLE_TIMEFRAMES[0]


def test_get_all_timeframes_and_events(service):
    service_inst, _, mock_event_timeframes_member_repo, *_ = service
    mock_event_timeframes_member_repo.get_all.return_value = SAMPLE_TIMEFRAMES
    result = service_inst.get_all_timeframes_and_events()
    mock_event_timeframes_member_repo.get_all.assert_called_once_with(select_query="*, events_member(*)")
    assert result == SAMPLE_TIMEFRAMES


def test_delete_timeframe(service):
    service_inst, _, mock_event_timeframes_member_repo, *_ = service
    mock_event_timeframes_member_repo.delete.return_value = None
    result = service_inst.delete_timeframe(timeframe_id=SAMPLE_TIMEFRAMES[0]["id"])
    mock_event_timeframes_member_repo.delete.assert_called_once_with(SAMPLE_TIMEFRAMES[0]["id"])
    assert result == {"statusCode": 200}
