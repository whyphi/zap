# TO BE COMPLETED: create service to perform analytics (used in API...)
from chalicelib.db import db


class InsightsService:
    def __init__(self):
        pass

    # def get(self, id: str):
    #     data = db.get_item(table_name="zap-applications", key={"applicantId": id})
    #     return data

    # def get_all(self):
    #     data = db.get_all(table_name="zap-applications")
    #     return data

    def get_insights_from_listing(self, id: str):
        data = db.get_applicants(table_name="zap-applications", listing_id=id)
        
        # iterate over each applicant and perform analytics
        return data


insights_service = InsightsService()
