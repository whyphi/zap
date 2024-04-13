from chalice import NotFoundError, BadRequestError
from chalicelib.modules.google_sheets import GoogleSheetsModule


class AccountabilityService:
    def __init__(self):
        # Currently hardcoded --> need to set as dynamic parameter either in DB or SSM
        self.spreadsheet_id = "1VEj06zGrxq-1Hrp8ArbYJkvPw58g5e4C3MhDeBjL6o4"
        self.gs = GoogleSheetsModule()

    def get_total_accountability(self, page: int, page_size: int = 20) -> dict[list]:
        START_ROW = 2 + page * page_size
        cells = self.gs.get_rows(
            spreadsheet_id=self.spreadsheet_id,
            sheet_name="Total",
            start_row=START_ROW,
            end_row=START_ROW + page_size - 1,
        )
        values = cells["values"]
        values = [
            {
                "name": f"{value[0]} {value[1]}",
                "status": value[2],
                "currentPoints": int(value[3]),
                "required": int(value[4]),
                "chapterBucketMet": True if "YES" == value[9] else False,
                "rushBucketMet": True if "YES" == value[10] else False,
                "fundraisingBucketMet": True if "YES" == value[11] else False,
                "eventsBucketMet": True if "YES" == value[12] else False,
                "teamsBucketMet": True if "YES" == value[13] else False,
                "variableBucketMet": True if "YES" == value[14] else False,
            }
            for value in values
        ]
        return values

    def get_accountability_from_leaderboard(self) -> dict[list]:
        cells = self.gs.get_all_cells(self.spreadsheet_id, "Leaderboard")
        values = cells["values"][1:]
        values = [
            {"name": f"{value[1]} {value[2]}", "score": value[3]} for value in values
        ]
        return values


accountability_service = AccountabilityService()
