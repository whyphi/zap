# TO BE COMPLETED: create service to perform analytics (used in API...)
from chalicelib.repositories.repository_factory import RepositoryFactory, RepositoryConfig
from chalice.app import BadRequestError
from typing import List

class InsightsService:
    def __init__(self):
         self.applications_repo = RepositoryFactory.applications()

    def get_insights_from_listing(self, id: str):
        """driver function of insights (returns both `dashboard` and `distribution`)"""
        try:
            # fetch applicants from `get_applicants` endpoint in `db.py`
            data = self.applications_repo.get_all_by_field("listing_id", listing_id)

            # call helper functions
            # NOTE: `get_dashboard_insights` updates the data object to ensure all majors/minors are Title() cased
            dashboard = self._get_dashboard_insights(data)
            distribution = self._get_pie_chart_insights(data)

            return dashboard, distribution
        except Exception as e:
            raise BadRequestError("Failed to get insights")

    # private method (kinda)
    def _get_dashboard_insights(self, data: List[dict]) -> dict:
        # initialize metrics
        majors = {}
        grad_years = {}
        num_applicants = len(data)
        avg_gpa = 0
        count_gpa = 0

        if num_applicants == 0:
            return {
                "applicantCount": 0,
                "avgGpa": "N/A",
                "commonMajor": "N/A",
                "commonGradYear": "N/A",
        }

        # iterate over each applicant and perform analytics
        for applicant in data:
            # convert major/minor to title case
            applicant["major"] = applicant["major"].title()
            applicant["minor"] = applicant["minor"].title()

            gpa = applicant.get("gpa", "")
            grad_year = applicant.get("gradYear", "")
            major = applicant.get("major", "")

            # attempt conversions (if fail, then skip)
            try:
                float_gpa = float(gpa)
                avg_gpa += float_gpa
                count_gpa += 1
            except ValueError:
                print("skipping gpa: ", gpa)
                pass
            try:
                float_grad = float(grad_year)
                grad_years[float_grad] = grad_years.get(float_grad, 0) + 1
            except ValueError:
                print("skipping gradYear: ", grad_year)
                pass

            # parse majors (if non-empty)
            if major:
                majors[major] = majors.get(major, 0) + 1

        if count_gpa:
            avg_gpa /= count_gpa
        else:
            avg_gpa = "N/A"

        # calculate most common major/gradYear
        # Check if majors dictionary is not empty
        if majors:
            common_major, _ = max(majors.items(), key=lambda x: x[1])
        else:
            # Handle the case when majors dictionary is empty
            common_major, _ = "N/A", 0

        # Check if grad_years dictionary is not empty
        if grad_years:
            common_grad_year, _ = max(grad_years.items(), key=lambda x: x[1])
        else:
            # Handle the case when grad_years dictionary is empty
            common_grad_year, _ = "N/A", 0

        dashboard = {
            "applicantCount": num_applicants,
            "avgGpa": round(avg_gpa, 1) if avg_gpa != "N/A" else avg_gpa,
            # "countCommonMajor": count_common_major,         # TO-DO: maybe do something with common major counts
            "commonMajor": common_major.title() if common_major != "N/A" else common_major,
            "commonGradYear": int(common_grad_year)
            if common_grad_year != "N/A"
            else common_grad_year,
            # "avgResponseLength": 0                        # TO-DO: maybe implement parsing for response lengths
        }

        return dashboard

    def _get_pie_chart_insights(self, data):
        """helper function for pie charts (should be function, not method within InsightsService)"""

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
        fields = [
            "colleges",
            "gpa",
            "gradYear",
            "major",
            "minor",
            "linkedin",
            "website",
        ]

        def findInsightsObject(metric, metric_val):
            """helper to the helper lol -> checks for previously added metric_name"""
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
                    val = "N/A" if (not val or val == "N/A") else "hasURL"

                # case 3: handle other metrics with mepty val (attempt to handle some edge cases)       # TO-DO: update Form.tsx in frontend to prevent bad inputs
                elif metric in ["minor", "gpa"] and (
                    not val or val.lower() in ["na", "n/a", "n a", "n / a"]
                ):
                    # general case
                    val = "N/A"

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
                            newCollege = {
                                "name": college,
                                "value": 1,
                                "applicants": [applicant],
                            }
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
