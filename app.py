from chalice import Chalice
from chalicelib.db import DBResource
from chalicelib.s3 import S3Client
from chalicelib.utils import get_image_extension_from_base64

import uuid

app = Chalice(app_name="zap")
db = DBResource()
s3 = S3Client()


@app.route("/")
def index():
    return {"hello": "world"}


@app.route("/submit", methods=["POST"])
def submit_form():
    # Get data as JSON and attach unique id for applicantId
    data = app.current_request.json_body
    applicant_id = str(uuid.uuid4())
    data["applicantId"] = applicant_id

    # Upload resume and retrieve, then set link to data
    resume_path = f"resume/{data['lastName']}_{data['firstName']}_{applicant_id}.pdf"
    resume_url = s3.upload_binary_data(resume_path, data["resume"])

    # Upload photo and retrieve, then set link to data
    image_extension = get_image_extension_from_base64(data["image"])
    image_path = f"image/{data['lastName']}_{data['firstName']}_{applicant_id}.{image_extension}"
    image_url = s3.upload_binary_data(image_path, data["image"])


    data["resume"], data["image"] = resume_url, image_url

    db.put_data("zap-applications", data)

    return {"msg": True, "resumeUrl": resume_url}


"""
TODO: 
Submit form data to dynamodb and mongodb
save resume in S3 -> generate link

"""
