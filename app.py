from chalice import Chalice, NotFoundError, BadRequestError
from chalicelib.db import DBResource
from chalicelib.s3 import S3Client
from chalicelib.utils import get_file_extension_from_base64
from pydantic import ValidationError

from chalicelib.services.ListingService import listing_service


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
    return listing_service.create(app.current_request.json_body)


@app.route("/listings/{id}", methods=["GET"], cors=True)
def get_listing(id):
    """Gets a listing from id"""
    return listing_service.get(id)


@app.route("/listings", methods=["GET"], cors=True)
def get_all_listings():
    """Gets all listings available"""
    return listing_service.get_all()


@app.route("/listings/{id}", methods=["DELETE"], cors=True)
def delete_listing(id):
    """Deletes a listing with the given ID."""
    return listing_service.delete(id)


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
    return listing_service.toggle_visibility(id)


@app.route("/listings/{id}/update-field", methods=["PATCH"], cors=True)
def update_listing_field_route(id):
    from chalicelib.validators.listings import UpdateFieldRequest

    try:
        # Validate given field type
        request_body = app.current_request.json_body
        request_body = UpdateFieldRequest(**request_body)

        # Get field and value from object
        field = request_body.field
        new_value = request_body.value

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

    except ValidationError as e:
        # https://aws.github.io/chalice/topics/views.html
        app.log.error(f"An error occurred: {str(e)}")
        raise BadRequestError(str(e))

    except NotFoundError as e:
        app.log.error(f"An error occurred: {str(e)}")
        return {"status": False, "message": str(e)}, 404

    except Exception as e:
        app.log.error(f"An error occurred: {str(e)}")
        return {"status": False, "message": "Internal Server Error"}, 500
