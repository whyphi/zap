import requests
from chalicelib.modules.aws_ssm import aws_ssm
import uuid


class MonitoringService:

    def __init__(self):
        try:
            self.api_key = aws_ssm.get_parameter_value("/Vault/POSTHOG_API_KEY")
            self.project_id = aws_ssm.get_parameter_value("/Vault/POSTHOG_PROJECT_ID")

        except Exception as e:
            print(e)

    def get_top_10_visited_pages(self):
        """
        Retrieves the top 10 visited pages from the PostHog API.

        Returns:
            dict: A dictionary containing the top 10 visited pages, with each page represented as a dictionary
            with the keys "name" and "value". The "name" key corresponds to the URL of the page, and the "value" key
            corresponds to the number of unique sessions for that page.

        Raises:
            requests.exceptions.RequestException: If there is an error making the API request.
        """
        # Make a POST request to the PostHog API to retrieve the top 10 visited pages
        query_response = requests.post(
            f"https://us.posthog.com/api/projects/{self.project_id}/query/",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                # The query to be executed
                "query": {
                    "kind": "TrendsQuery",
                    "properties": {
                        # Filter the events to only include those that correspond to page views
                        "type": "AND",
                        "values": [
                            {
                                "type": "AND",
                                "values": [
                                    {
                                        "key": "$current_url",
                                        "type": "event",
                                        "value": "?",
                                        "operator": "not_icontains",
                                    }
                                ],
                            }
                        ],
                    },
                    # Filter out test accounts when retrieving the data
                    "filterTestAccounts": True,
                    # Only retrieve data from the past 30 days
                    "dateRange": {"date_from": "-30d"},
                    # The events to retrieve
                    "series": [
                        {
                            "kind": "EventsNode",
                            "event": "$pageview",
                            # The name of the event
                            "name": "$pageview",
                            # How to aggregate the data
                            "math": "unique_session",
                        }
                    ],
                    # The time interval to group the data by
                    "interval": "day",
                    # How to group the data
                    "breakdownFilter": {
                        "breakdown_type": "event",
                        "breakdown": "$current_url",
                    },
                    # How to display the data
                    "trendsFilter": {"display": "ActionsBarValue"},
                },
                # A unique identifier for the query
                "client_query_id": str(uuid.uuid4()),
                # Whether to refresh the cache
                "refresh": True,
                # Whether to execute the query asynchronously
                "async": False,
            },
        )

        # Parse the response as JSON
        query_data = query_response.json()

        # Sort the results by the number of unique sessions in descending order
        top_website_pages_result = sorted(
            [
                # For each event, create a dictionary with the page URL and the number of unique sessions
                {"name": data["label"], "value": data["aggregated_value"]}
                for data in query_data["results"]
                # Only include events that correspond to a page URL
                if data["label"].startswith("https")
            ],
            key=lambda x: -x["value"],
        )[:10]

        # Return the top 10 visited pages
        return {"topWebsitePages": top_website_pages_result}


monitoring_service = MonitoringService()
