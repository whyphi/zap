# TO BE COMPLETED: create service to perform analytics (used in API...)
from chalicelib.db import db


class InsightsService:
    def __init__(self):
        pass

    def get_insights_from_listing(self, id: str):
        data = db.get_applicants(table_name="zap-applications", listing_id=id)

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
        commonMajor, count = "", 0

        # update most common major
        for major, freq in majors.items():
            if freq > count:
                commonMajor = major
                count = freq

        insights = {
            "applicantCount": num_applicants,
            "avgGpa": avgGpa,
            "commonMajor": commonMajor,
            "countCommonMajor": count,
            "avgGradYear": avgGradYear,
            "avgResponseLength": 0
        }
        
        return insights, data


insights_service = InsightsService()
