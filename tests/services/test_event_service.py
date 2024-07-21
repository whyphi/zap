# import pytest
# from unittest.mock import MagicMock, patch
# from zap.chalicelib.services.EventsMemberService import EventService
# import datetime
# import json

# with open("tests/fixtures/events/general/sample_timeframes.json") as f:
#     SAMPLE_TIMEFRAMES: list = json.load(f)

# with open("tests/fixtures/events/general/sample_timeframe_sheets.json") as f:
#     SAMPLE_TIMEFRAME_SHEETS: list = json.load(f)

# with open("tests/fixtures/events/general/sample_rush_events.json") as f:
#     SAMPLE_RUSH_EVENTS: list = json.load(f)

# with open("tests/fixtures/events/general/sample_rush_event.json") as f:
#     SAMPLE_RUSH_EVENT = json.load(f)

# @pytest.fixture
# def mock_mongo_module():
#     with patch("chalicelib.modules.mongo.MongoModule", autospec=True) as MockMongoModule:
#         mock_instance = MockMongoModule(use_mock=True)
#         yield mock_instance

# @pytest.fixture
# def event_service(mock_mongo_module):
#     return EventService(mock_mongo_module)

# def test_insert_document(event_service, mock_mongo_module):
#     CREATE_TIMEFRAME = { "name": "testTimeframeName", "spreadsheetId": "testSpreadsheetId" }
#     date_created = datetime.datetime.now()

#     with patch("chalicelib.services.EventService.datetime") as mock_datetime:
#         mock_datetime.datetime.now.return_value = date_created
#         result = event_service.create_timeframe(CREATE_TIMEFRAME)
#         CREATE_TIMEFRAME["date_created"] = date_created
#         mock_mongo_module.insert_document.assert_called_once_with(
#             collection="events-timeframe", data=CREATE_TIMEFRAME
#         )

#         assert result == {"msg": True}

# def test_get_timeframe(event_service, mock_mongo_module):
#     mock_mongo_module.get_document_by_id.return_value = SAMPLE_TIMEFRAMES[0]
#     timeframe_id = SAMPLE_TIMEFRAMES[0]["_id"]
 
#     result = event_service.get_timeframe(timeframe_id=timeframe_id)
#     mock_mongo_module.get_document_by_id.assert_called_once_with(
#         collection="events-timeframe", document_id=timeframe_id
#     )

#     assert result == json.dumps(SAMPLE_TIMEFRAMES[0])

# def test_get_all_timeframe(event_service, mock_mongo_module):
#     mock_mongo_module.get_all_data_from_collection.return_value = SAMPLE_TIMEFRAMES
 
#     result = event_service.get_all_timeframes()
#     mock_mongo_module.get_all_data_from_collection.assert_called_once_with(
#         collection="events-timeframe"
#     )

#     assert result == json.dumps(SAMPLE_TIMEFRAMES)

# def test_delete_timeframe(event_service, mock_mongo_module):
#     result = event_service.delete_timeframe(timeframe_id=SAMPLE_TIMEFRAMES[0]["_id"])
#     assert result["statusCode"] == 200


# # TODO: potentially add mocking for GoogleSheetsModule (otherwise test is not isolated)
# # def test_create_event(event_service, mock_mongo_module):
# #     CREATE_TIMEFRAME = { "name": "eventName", "tags": "tags", "sheetTab": "selectedSheetTab" }
# #     date_created = datetime.datetime.now()
# #     timeframe_id = "timeframeId"

# # TODO:

# # def get_event(self, event_id: str):

# # def checkin(self, event_id: str, user: dict) -> dict:

# # def delete(self, event_id: str):

# # def get_timeframe_sheets(self, timeframe_id: str):

# # def get_rush_categories_and_events(self):

# # def create_rush_category(self, data: dict):

# # def create_rush_event(self, data: dict):

# # def modify_rush_event(self, data: dict):

# # def modify_rush_settings(self, data: dict):

# # def get_rush_event(self, event_id: str, hide_attendees: bool = True):

# # def checkin_rush(self, event_id: str, user_data: dict):

# # def delete_rush_event(self, event_id: str):
