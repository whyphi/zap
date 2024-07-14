import pytest
from unittest.mock import MagicMock, patch
from chalicelib.services.EventService import EventService
import datetime


@pytest.fixture
def mock_mongo_module():
    with patch("chalicelib.modules.mongo.MongoModule", autospec=True) as MockMongoModule:
        mock_instance = MockMongoModule(use_mock=True)
        yield mock_instance

@pytest.fixture
def event_service(mock_mongo_module):
    return EventService(mock_mongo_module)


def test_insert_document(event_service, mock_mongo_module):
    CREATE_TIMEFRAME = { "name": "testTimeframeName", "spreadsheetId": "testSpreadsheetId" }
    dateCreated = datetime.datetime.now()

    with patch("chalicelib.services.EventService.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = dateCreated
        result = event_service.create_timeframe(CREATE_TIMEFRAME)
        CREATE_TIMEFRAME["dateCreated"] = dateCreated
        mock_mongo_module.insert_document.assert_called_once_with(
            collection="events-timeframe", data=CREATE_TIMEFRAME
        )

        assert result == {"msg": True}