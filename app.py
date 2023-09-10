from chalice import Chalice
from chalicelib.db import DBResource
from chalicelib.s3 import S3Client
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
    resume_url = s3.upload_resume(resume_path, data["resume"])
    data["resume"] = resume_url

    db.put_data("zap-applications", data)

    return {"msg": True, "resumeUrl": resume_url}


"""
TODO: 
Submit form data to dynamodb and mongodb
save resume in S3 -> generate link

"""
