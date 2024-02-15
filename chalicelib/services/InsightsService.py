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
        # NOTE: `get_dashboard_insights` updates the data object to ensure all majors/minors are Title() cased
        dashboard = InsightsService._get_dashboard_insights(data)
        distribution = InsightsService._get_pie_chart_insights(data)

        return dashboard, distribution

    # private method (kinda)
    def _get_dashboard_insights(data):
        # initialize metrics
        majors = {}
        num_applicants = len(data)
        avg_gpa, avg_grad_year = 0, 0
        count_gpa = 0

        # iterate over each applicant and perform analytics
        for applicant in data:
            # convert major/minor to title case
            applicant["major"] = applicant["major"].title()
            applicant["minor"] = applicant["minor"].title()

            gpa, grad_year, major = applicant["gpa"], applicant["gradYear"], applicant["major"]

            # attempt conversions (if fail, then skip)
            try:
                float_gpa = float(gpa)
                avg_gpa += float_gpa
                count_gpa += 1
            except ValueError:
                pass
            try:
                float_grad = float(grad_year)
                avg_grad_year += float_grad
            except ValueError:
                pass
            
            # parse majors (if non-empty)
            if major:
                if major in majors:
                    majors[major] += 1
                else:
                    majors[major] = 1
        
        avg_gpa /= count_gpa
        avg_grad_year /= num_applicants
        common_major, count_common_major = "", 0

        # update most common major
        for major, freq in majors.items():
            if freq > count_common_major:
                common_major = major
                count_common_major = freq

        dashboard = {
            "applicantCount": num_applicants,
            "avgGpa": round(avg_gpa, 1),                     # round to 1 decimal place (e.g. 3.123 -> 3.1)
            "commonMajor": common_major.title(),
            # "countCommonMajor": count_common_major,         # TO-DO: maybe do something with common major counts
            "avgGradYear": int(avg_grad_year),
            # "avgResponseLength": 0                        # TO-DO: maybe implement parsing for response lengths
        }

        return dashboard


    def _get_pie_chart_insights(data):
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
            # check if college exists in `distribution["colleges"]`
            found_object = None

            for distribution_object in distribution[metric]:
                if distribution_object["name"] == metric_val:
                    found_object = distribution_object
                    break
            
            return found_object

        for applicant in data:
            # iterate over applicant dictionary
            for metric, val in applicant.items():

                # case 1: ignore irrelevant metrics
                if metric not in fields:
                    continue
                
                # case 2: metric is a url
                if metric in ["linkedin", "website"]:
                    val = 'N/A' if (not val or val == 'N/A') else 'True'
                 
                # case 3: handle other metrics with mepty val (attempt to handle some edge cases)       # TO-DO: update Form.tsx in frontend to prevent bad inputs
                elif metric in ['minor', 'gpa'] and (not val or val.lower() in ['na', 'n/a', 'n a',  'n / a']):
                    # general case
                    val = 'N/A'
                
                # case 4: colleges -> iterate over colleges object
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
                
                # handle remaining fields
                found_object = findInsightsObject(metric, val)
                        
                if found_object:
                    found_object["value"] += 1
                    found_object["applicants"] += [applicant]
                else:
                    new_object = {"name": val, "value": 1, "applicants": [applicant]}
                    distribution[metric] += [new_object]

        return distribution


insights_service = InsightsService()
