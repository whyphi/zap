from chalicelib.db import db


class ApplicantService:
    def __init__(self):
        pass

    def get(self, id: str):
        data = db.get_item(table_name="zap-applications", key={"applicantId": id})
        return data

    def get_all(self):
        data = db.get_all(table_name="zap-applications")
        return data

    def get_all_from_listing(self, id: str):
        data = db.get_applicants(table_name="zap-applications", listing_id=id)
        return data


applicant_service = ApplicantService()
