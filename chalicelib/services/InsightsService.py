# TO BE COMPLETED: create service to perform analytics (used in API...)
from chalicelib.db import db


class InsightsService:
    def __init__(self):
        pass

    def get_insights_from_listing(self, id: str):

        ''' driver function of insights (returns both `dashboard` and `distribution`) '''

        # fetch applicants from `get_applicants` endpoint in `db.py`
        data = db.get_applicants(table_name="zap-applications", listing_id=id)

        # call helper functions
        dashboard = InsightsService.get_dashboard_insights(data)
        distribution = InsightsService.get_pie_chart_insights(data)

        return dashboard, distribution
    

    def get_dashboard_insights(data):
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

        dashboard = {
            "applicantCount": num_applicants,
            "avgGpa": round(avgGpa, 1),                     # round to 1 decimal place (e.g. 3.123 -> 3.1)
            "commonMajor": commonMajor,
            # "countCommonMajor": countCommonMajor,         # TO-DO: maybe do something with common major counts
            "avgGradYear": int(avgGradYear),
            # "avgResponseLength": 0                        # TO-DO: maybe implement parsing for response lengths
        }

        return dashboard


    def get_pie_chart_insights(data):
        ''' helper function for pie charts (should be function, not method within InsightsService) '''

        # initialize return object
        # value (list) structure : [ {name: string, value: int, applicants: Applicant[]}, ... , ... ]
        distribution = {
            "colleges": [],
            "gpa": [],
            "gradYear": [],
            "major": [],
            "minor": [],
            "linkedin": [],
            "website": [],
        }
    
        # list of fields we want to consider
        fields = ["colleges", "gpa", "gradYear", "major", "minor", "linkedin", "website"]

        def findInsightsObject(metric, metric_val):
            ''' helper to the helper lol -> checks for previously added metric_name '''
            # if not val:
            print("####", metric, metric_val)
            # check if college exists in `distribution["colleges"]`
            found_object = None

            for distributionObject in distribution[metric]:
                if distributionObject["name"] == metric_val:
                    found_object = distributionObject
                    break
            
            return found_object

        for applicant in data:
            # iterate over applicant dictionary
            for metric, val in applicant.items():
                # redefine value if empty
                val = 'False' if not val else val

                # case 1: ignore irrelevant metrics
                if metric not in fields:
                    continue
                
                # case 2: colleges -> iterate over colleges object
                elif metric == "colleges":
                    for college, status in val.items():
                        # edge case: if status is false, skip (shouldn't contribute to count)
                        if not status:
                            continue

                        # check if college exists in `distribution["colleges"]`
                        found_college = findInsightsObject(metric, college)
                        
                        if found_college:
                            found_college["value"] += 1
                            found_college["applicants"] += [applicant]
                        else:
                            newCollege = {"name": college, "value": 1, "applicants": [applicant]}
                            distribution[metric] += [newCollege]

                        # skip to next metric
                    continue 
                        

                # case 3: links -> linkedin or website
                elif metric in ["linkedin", "website"]:
                    val = 'True' if val else 'False'
                
                # handle remaining fields
                found_object = findInsightsObject(metric, val)
                        
                if found_object:
                    found_object["value"] += 1
                    found_object["applicants"] += [applicant]
                else:
                    newObject = {"name": val, "value": 1, "applicants": [applicant]}
                    distribution[metric] += [newObject]

        return distribution


insights_service = InsightsService()
