# TO BE COMPLETED: create service to perform analytics (used in API...)
from chalicelib.db import db


class InsightsService:
    def __init__(self):
        pass

    # TO-DO: helper function for pie charts

    def get_insights_from_listing(self, id: str):
        # fetch applicants from `get_applicants` endpoint in `db.py`
        data = db.get_applicants(table_name="zap-applications", listing_id=id)

        # TO-DO: call helper function to get distribution stats (for pie charts)

        # initialize metrics
        majors = {}
        num_applicants = len(data)
        avgGpa, avgGradYear = 0, 0

        # iterate over each applicant and perform analytics
        for applicant in data:
            gpa, gradYear, major = applicant["gpa"], applicant["gradYear"], applicant["major"]

            # attempt conversions (if fail, then skip)
            try:
                floatGpa = float(gpa)
                avgGpa += floatGpa
            except ValueError:
                pass
            try:
                floatGrad = float(gradYear)
                avgGradYear += floatGrad
            except ValueError:
                pass
            
            # parse majors (if non-empty)
            if major:
                if major in majors:
                    majors[major] += 1
                else:
                    majors[major] = 1
        
        avgGpa /= num_applicants
        avgGradYear /= num_applicants
        commonMajor, countCommonMajor = "", 0

        # update most common major
        for major, freq in majors.items():
            if freq > countCommonMajor:
                commonMajor = major
                countCommonMajor = freq

        insights = {
            "applicantCount": num_applicants,
            "avgGpa": round(avgGpa, 1),                     # round to 1 decimal place (e.g. 3.123 -> 3.1)
            "commonMajor": commonMajor,
            # "countCommonMajor": countCommonMajor,         # TO-DO: maybe do something with common major counts
            "avgGradYear": int(avgGradYear),
            # "avgResponseLength": 0                        # TO-DO: maybe implement parsing for response lengths
        }
        
        return insights


insights_service = InsightsService()
