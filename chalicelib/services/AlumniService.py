from chalicelib.db import db

import uuid


class AlumniService:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def create(self, data):
        print(data)
        # db.put_data(self.table_name, data)
        pass

    def get_all(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass


alumni_service = AlumniService(table_name="zap-alumni")
