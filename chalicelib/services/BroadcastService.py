from chalicelib.modules.google_sheets import GoogleSheetsModule
from chalicelib.modules.ses import ses, SesDestination
from typing import List, Dict

class BroadcastService:
    def __init__(self):
        self.gs = GoogleSheetsModule()
        self.JOBS_SHEET_ID = "1-KgZeWxiBn35ARMaZPYJkUJnYTVbfGpiVjxwwKP2jCQ"  # Add this to SSM later
        
    def parse_job_types(self, type_string: str) -> List[str]:
        """Parse the comma-separated type string into categories"""
        if not type_string:
            return []
        
        types = [t.strip() for t in type_string.split(',')]
        return types
        
    def fetch_job_listings(self) -> Dict[str, List[Dict]]:
        """Fetches job listings and categorizes them by type"""
        try:
            response = self.gs.get_all_cells(self.JOBS_SHEET_ID, "2026 - Business")  
            if not response.get("values"):
                return {
                    "jobs": {}
                }            
            headers = response["values"][3]
            rows = response["values"][4:] 
            
            # Initialize categories
            categorized_jobs = {
                "Tech": [],
                "Finance": [],
                "Consulting": [],
                "Marketing": [],
                "Other": []
            }
            
            recognized_categories = ["Tech", "Finance", "Consulting", "Marketing"]
            
            for row in rows:
                job_data = dict(zip(headers, row))

                # clean up description
                job_data["Description"] = " ".join(job_data.get("Description", "").split())

                # e.g. "Software,Technology" → ["Software", "Technology"]
                type_string = job_data.get("Type", "") or ""
                types = self.parse_job_types(type_string)

                matched_any_category = False
                lower_types = [t.lower() for t in types]

                for cat in recognized_categories:
                    cat_lower = cat.lower()

                    # if ANY of the job's type strings contains the category substring
                    # e.g. "technology" contains "tech"
                    if any(cat_lower in t for t in lower_types):
                        categorized_jobs[cat].append(job_data)
                        matched_any_category = True
                        # no 'break' here if you want multi-category matching
                        # if you want only the *first* category match, then uncomment the break:
                        # break

            if not matched_any_category:
                categorized_jobs["Other"].append(job_data)
                            
            # Remove empty categories
            return {
                "jobs": {k: v for k, v in categorized_jobs.items() if v}
            }
                
        except Exception as e:
            return {
                "jobs": {}
            }
    
    def generate_job_html(self, jobs: Dict[str, List[Dict]]) -> str:
        """Generates HTML for job listings"""
        html = "<div class='jobs-section'>"
        html += "<h2>Job Opportunities</h2>"
        
        for category, listings in jobs.items():
            if listings:  # Only show categories with jobs
                html += f"<div class='category-section'>"
                html += f"<h3>{category}</h3>"
                html += "<ul class='job-list'>"
                
                for job in listings:
                    year = job.get("Year", "N/A")
                    company = job.get("Company", "N/A")
                    description = job.get("Description", "N/A")
                    link = job.get("Link", "#")
                    
                    html += f"""
                        <li class='job-item'>
                            <div class='job-header'>
                                <a href='{link}' target='_blank' class='company-name'>
                                    <strong>{company}</strong>
                                </a>
                                <span class='year'>({year})</span>
                            </div>
                            <p class='job-description'>{description}</p>
                        </li>
                    """
                
                html += "</ul></div>"
        
        html += "</div>"
        return html
    
    def generate_newsletter_content(self, custom_content: str = "") -> Dict:
        """Generates the complete newsletter content"""
        jobs = self.fetch_job_listings()
        jobs_html = self.generate_job_html(jobs)
        
        # Combine all content with custom CSS
        css = """
        <style>
            .jobs-section { margin: 20px 0; }
            .category-section { margin: 15px 0; }
            .job-list { list-style-type: none; padding-left: 0; }
            .job-item { 
                margin-bottom: 15px;
                padding: 10px;
                border-left: 3px solid #007bff;
                background-color: #f8f9fa;
            }
            .job-header { margin-bottom: 5px; }
            .company-name { color: #007bff; text-decoration: none; }
            .year { color: #6c757d; margin-left: 10px; }
            .job-description { margin: 5px 0; color: #212529; }
        </style>
        """
        
        full_html = f"""
        {css}
        <div class="newsletter">
            <div class="custom-content">
                {custom_content}
            </div>
            
            {jobs_html}
        </div>
        """
        
        return {
            "html": full_html,
            "raw_data": {
                "jobs": jobs
            }
        }
    
    def send_newsletter(self, subject: str, content: str, recipients: List[str]) -> None:
        """Sends the newsletter to specified recipients"""
        for email in recipients:
            ses_destination = SesDestination(tos=[email])
            ses.send_email(
                source="techteampct@gmail.com",
                destination=ses_destination,
                subject=subject,
                text=content,  # Plain text version
                html=content   # HTML version
            )
            
broadcast_service = BroadcastService()  