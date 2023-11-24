from chalice import Chalice, NotFoundError
from chalicelib.db import DBResource
from chalicelib.s3 import S3Client
from chalicelib.utils import get_file_extension_from_base64


import uuid

app = Chalice(app_name="zap")
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


@app.route("/create", methods=["POST"], cors=True)
def create_listing():
    """Creates a new listing with given information"""
    data = app.current_request.json_body
    listing_id = str(uuid.uuid4())
    data["listingId"] = listing_id
    data["isVisible"] = True

    db.put_data(table_name="zap-listings", data=data)

    return {"msg": True}


@app.route("/listings", methods=["GET"], cors=True)
def get_all_listings():
    """Gets all listings available"""
    data = db.get_all(table_name="zap-listings")
    return data


@app.route("/listings/{id}", methods=["GET"], cors=True)
def get_listing(id):
    """Gets a listing from id"""
    data = db.get_item(table_name="zap-listings", key={"listingId": id})

    return data

@app.route("/listings/{id}", methods=["DELETE"], cors=True)
def delete_listing(id):
    """Deletes a listing with the given ID."""
    try:
        # Perform delete operation in the database
        deleted_listing = db.delete_item(table_name="zap-listings", key={"listingId": id})

        # Check the result and return the appropriate response
        if deleted_listing:
            return {"status": True}
        else:
            raise NotFoundError("Listing not found")

    except NotFoundError as e:
        app.log.error(f"An error occurred: {str(e)}")
        return {"status": False, "message": "Listing not found"}, 404

    except Exception as e:
        app.log.error(f"An error occurred: {str(e)}")
        return {"status": False, "message": "Internal Server Error"}, 500


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


@app.route("/listings/{id}/toggle/visibility", methods=["PATCH"], cors=True)
def toggle_visibility(id):
    """Toggles visibilility of a given <listing_id>"""
    try:
        # Perform visibility toggle in the database
        data = db.toggle_visibility(table_name="zap-listings", key={"listingId": id})

        # Check the result and return the appropriate response
        if data:
            return {"status": True}
        else:
            return {"status": False,  "message": "Invalid listing ID"}, 400

    except Exception as e:
        app.log.error(f"An error occurred: {str(e)}")
        return {"status": False, "message": "Internal Server Error"}, 500
    
@app.route("/listings/{id}/update-field", methods=["PATCH"], cors=True)
def update_listing_field_route(id):
    try:
        # Get the field and the new value from the request body
        request_body = app.current_request.json_body
        field = request_body.get("field")
        new_value = request_body.get("value")

        # Check if the listing exists
        existing_listing = db.get_item(table_name="zap-listings", key={"listingId": id})
        if not existing_listing:
            raise NotFoundError("Listing not found")

        # Update the specified field in the database
        updated_listing = db.update_listing_field(
            table_name="zap-listings",
            key={"listingId": id},
            field=field,
            new_value=new_value,
        )

        # Check the result and return the appropriate response
        if updated_listing:
            return {"status": True, "updated_listing": updated_listing}
        else:
            raise NotFoundError("Listing not found")

    except NotFoundError as e:
        app.log.error(f"An error occurred: {str(e)}")
        return {"status": False, "message": str(e)}, 404

    except Exception as e:
        app.log.error(f"An error occurred: {str(e)}")
        return {"status": False, "message": "Internal Server Error"}, 500