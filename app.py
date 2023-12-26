from chalice import Chalice
from chalicelib.db import DBResource
from chalicelib.s3 import S3Client
from chalicelib.utils import get_file_extension_from_base64

import uuid

from chalicelib.api.listings import listings_api

app = Chalice(app_name="zap")
app.register_blueprint(listings_api)

db = DBResource()
s3 = S3Client()


@app.route("/")
def index():
    return {"hello": "world"}


@app.route("/test")
def test():
    return {"test": "test"}


@app.route("/submit", methods=["POST"], cors=True)
def submit_form():
    # Get data as JSON and attach unique id for applicantId
    data = app.current_request.json_body
    applicant_id = str(uuid.uuid4())
    data["applicantId"] = applicant_id

    # Upload resume and retrieve, then set link to data
    resume_path = f"resume/{data['listingId']}/{data['lastName']}_{data['firstName']}_{applicant_id}.pdf"
    resume_url = s3.upload_binary_data(resume_path, data["resume"])

    # Upload photo and retrieve, then set link to data
    image_extension = get_file_extension_from_base64(data["image"])
    image_path = f"image/{data['listingId']}/{data['lastName']}_{data['firstName']}_{applicant_id}.{image_extension}"
    image_url = s3.upload_binary_data(image_path, data["image"])

    # Reset data properties as S3 url
    data["resume"], data["image"] = resume_url, image_url

    # Upload data to DynamoDB
    db.put_data(table_name="zap-applications", data=data)

    return {"msg": True, "resumeUrl": resume_url}


@app.route("/applicants", methods=["GET"], cors=True)
def get_applicants():
    data = db.get_all(table_name="zap-applications")
    return data


@app.route("/applicant/{applicant_id}", methods=["GET"], cors=True)
def get_applicant(applicant_id):
    """Get an applicant from <applicant_id>"""
    data = db.get_item(table_name="zap-applications", key={"applicantId": applicant_id})
    return data


@app.route("/applicants/{listing_id}", methods=["GET"], cors=True)
def get_all_applicants(listing_id):
    """Gets all applicants from <listing_id>"""
    data = db.get_applicants(table_name="zap-applications", listing_id=listing_id)
    return data
