
from chalicelib.db import DBResource
from chalice import Blueprint
from chalicelib.api.spreadsheetapi import getdata, extractFileId


import uuid
accountability_api = Blueprint(__name__)
db = DBResource()

#Manager Semesters
@accountability_api.route("/semester",methods=["POST"],cors=True)
def add_semester():
    """add new semester with given information"""
    table_name = "zap-tracker"
    data = accountability_api.current_request.json_body

    listing_id = str(uuid.uuid4())
    data["semesterId"] = listing_id
    
    db.put_data(table_name, data)
    return {"msg":True}

@accountability_api.route("/semester/list",methods=["GET"],cors=True)
def semester_list():
    """get the list of semesters"""
    data = db.get_all(table_name="zap-tracker")
    return data

#Manage Google Spreadsheet API and Data
@accountability_api.route('/spreadsheet', methods=['POST'], cors=True)
def GoogleSheet():
    try:
        request_data = accountability_api.current_request.json_body
        url = request_data.get('link')

        fileId = extractFileId(url)
        datarange = 'Brothers'
        data = getdata(fileId, datarange)

        if data is None:
            return {'msg': False}

        return data  
    except Exception as e:
        return {'error': str(e)}, 500