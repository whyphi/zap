from chalicelib.modules.mongo import mongo_module

import json
from bson import ObjectId


class MemberService:
    class BSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self):
        self.collection = "users"

    def get_all(self):
        data = mongo_module.get_all_data_from_collection(self.collection)
        return json.dumps(data, cls=self.BSONEncoder)


member_service = MemberService()
