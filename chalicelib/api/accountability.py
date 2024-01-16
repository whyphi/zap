
from chalicelib.db import DBResource
from chalice import Blueprint
import spreadsheetapi


import uuid
accountability_api = Blueprint(__name__)
db = DBResource()

#Manager Semesters
@accountability_api.route("/semester",methods=["POST"],corse=True)
def add_semester():
    """add new semester with given information"""
    data = accountability_api.current_request.json_body

    listing_id = str(uuid.uuid4())
    data["listingId"] = listing_id
    
    db.put_data(table_name="semester-listing", data=data)
    return {"msg":True}

@accountability_api.route("/semester/list",methods=["GET"],corse=True)
def semester_list():
    """get the list of semesters"""
    data = db.get_all(table_name="semester-listing")
    return data

#Manage Google Spreadsheet API and Data
@accountability_api.route('/spreadsheet', methods=['POST'], cors=True)
def GoogleSheet():
    try:
        request_data = accountability_api.current_request.json_body
        url = request_data.get('link')

        fileId = spreadsheetapi.extractFileId(url)
        datarange = 'Brothers'
        data = spreadsheetapi.getdata(fileId, datarange)

        if data is None:
            return {'msg': False}

        return data  
    except Exception as e:
        return {'error': str(e)}, 500