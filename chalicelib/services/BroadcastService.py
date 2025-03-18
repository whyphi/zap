from chalicelib.modules.ses import ses, SesDestination
from chalicelib.services.JobPostingService import job_posting_service
from typing import List, Dict

class BroadcastService:
    def __init__(self):
        self.ps = job_posting_service
    
    def generate_job_html(self, jobs: List[Dict]) -> str:
        """Generates HTML for job listings based on the new job data format."""
        html = "<div class='jobs-section'>"
        html += "<h2>Job Opportunities</h2>"
        html += "<ul class='job-list'>"
        
        for job in jobs:
            company = job.get("company", "N/A")
            role = job.get("role", "N/A")
            link = job.get("link", "#")
            deadline = job.get("date", "N/A")
            
            job_line = (
                f"{company} | {role} | "
                f"<a href='{link}' target='_blank'>Link</a> | {deadline}"
            )
            
            html += f"<li class='job-item'>{job_line}</li>"
        
        html += "</ul></div>"
        return html

    def generate_newsletter_content(self, custom_content: str = "") -> Dict:
        """Generates the complete newsletter content"""
        # Call the updated getFinanceJobs() from the job posting service.
        finance_jobs = self.ps.getFinanceJobs()
        jobs_html = self.generate_job_html(finance_jobs)
        
        # Combine all content with custom CSS
        css = """
        <style>
            .jobs-section { margin: 20px 0; }
            .job-list { list-style-type: none; padding-left: 0; }
            .job-item { 
                margin-bottom: 15px;
                padding: 10px;
                border-left: 3px solid #007bff;
                background-color: #f8f9fa;
            }
            .job-header { margin-bottom: 5px; }
            .company-name { color: #007bff; text-decoration: none; }
            .deadline { color: #6c757d; margin-left: 10px; }
            .job-role { margin: 5px 0; color: #212529; }
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
                "jobs": finance_jobs
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
                html=content    # HTML version
            )

broadcast_service = BroadcastService()