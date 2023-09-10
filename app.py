from chalice import Chalice
from chalicelib.db import DBResource
import uuid

app = Chalice(app_name='test')
db = DBResource()

@app.route('/')
def index():
    return {'hello': 'world'}

@app.route("/submit", methods=["POST"])
def submit_form():

    # Get data as JSON and attach unique id for applicantId
    data = app.current_request.json_body
    applicant_id = str(uuid.uuid4())
    data["applicantId"] = applicant_id
    
    db.put_data("zap-applications", data)

    
    return {
        "msg": True
    }

"""
TODO: 
Submit form data to dynamodb and mongodb
save resume in S3 -> generate link

"""