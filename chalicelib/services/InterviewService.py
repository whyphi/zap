from chalicelib.modules.mongo import mongo_module
from chalice import NotFoundError, BadRequestError, UnauthorizedError
import json
from bson import ObjectId
import datetime
from chalicelib.modules.ses import ses, SesDestination


class InterviewService:
    class BSONEncoder(json.JSONEncoder):
        """JSON encoder that converts Mongo ObjectIds and datetime.datetime to strings."""

        def default(self, o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            elif isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self):
        self.collection_prefix = "interviews-"

    def create_interview(self, interview_data: dict):
        interview_data["dateCreated"] = datetime.datetime.now()
        mongo_module.insert_document(
            f"{self.collection_prefix}listings", interview_data
        )

    def get_interview_listing(self, interview_id: str):
        interview_listing = mongo_module.get_document_by_id(
            f"{self.collection_prefix}listings", interview_id
        )
        return json.dumps(interview_listing, cls=self.BSONEncoder)

    def get_all_interviews(self):
        """Retrieve all interviews from the database."""
        interviews = mongo_module.get_all_data_from_collection(
            f"{self.collection_prefix}listings"
        )
        return json.dumps(interviews, cls=self.BSONEncoder)

    def delete_interview_listing(self, interview_id: str):
        interview_listing = mongo_module.get_document_by_id(
            f"{self.collection_prefix}listings", interview_id
        )
        if interview_listing is None:
            raise NotFoundError(
                f"Interview Listing with ID {interview_id} does not exist."
            )

        # Delete all the interview responses related to that interview listing
        for response_id in interview_listing["response_ids"]:
            mongo_module.delete_document_by_id(
                f"{self.collection_prefix}responses", response_id
            )

        # Delete the interview listing itself
        mongo_module.delete_document_by_id(
            f"{self.collection_prefix}listings", interview_id
        )


interview_service = InterviewService()
