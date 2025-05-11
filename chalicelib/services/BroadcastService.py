from chalicelib.modules.ses import ses, SesDestination
from chalicelib.services.JobPostingService import job_posting_service
from typing import List, Dict

class BroadcastService:
    def __init__(self):
        self.ps = job_posting_service
    
    def generate_section_html(self, section_title: str, jobs: List[Dict]) -> str:
        """
        Generates an HTML section for a given list of jobs.
        """
        html = f"<div class='jobs-section'><h2>{section_title} Opportunities</h2><ul class='job-list'>"
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
        """
        Generates a complete newsletter with four sections:
            - Finance: Data from Google Sheets
            - Tech: Jobs from SimplifyJobs and cvrve GitHub repos
            - Consulting: Jobs from jobright-ai Consultant GitHub repo
            - Marketing: Jobs from jobright-ai Marketing GitHub repo
        
        Returns:
            Dict: A dictionary with HTML content and the raw job data.
        """
        # Finance jobs from Google Sheets
        finance_jobs = self.ps.getFinanceJobs()
        
        # Tech jobs: Merge data from both Simplify and Crve GitHub repos
        tech_jobs_simplify = self.ps.getJobs("https://github.com/SimplifyJobs/Summer2025-Internships/blob/dev/README.md")
        tech_jobs_cvre = self.ps.getJobs("https://github.com/cvrve/Summer2025-Internships/blob/dev/README.md")
        tech_jobs = tech_jobs_simplify + tech_jobs_cvre
        
        # Consulting jobs from jobright-ai Consultant GitHub repo
        consulting_jobs = self.ps.getJobs("https://github.com/jobright-ai/2025-Consultant-Internship/blob/master/README.md")
        
        # Marketing jobs from jobright-ai Marketing GitHub repo
        marketing_jobs = self.ps.getJobs("https://github.com/jobright-ai/2025-Marketing-Internship/blob/master/README.md")
        
        # Generate HTML for each section
        finance_section = self.generate_section_html("Finance", finance_jobs)
        tech_section = self.generate_section_html("Tech", tech_jobs)
        consulting_section = self.generate_section_html("Consulting", consulting_jobs)
        marketing_section = self.generate_section_html("Marketing", marketing_jobs)
        
        # Common CSS for styling the newsletter sections
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
            {finance_section}
            {tech_section}
            {consulting_section}
            {marketing_section}
        </div>
        """
        
        return {
            "html": full_html,
            "raw_data": {
                "finance_jobs": finance_jobs,
                "tech_jobs": tech_jobs,
                "consulting_jobs": consulting_jobs,
                "marketing_jobs": marketing_jobs
            }
        }
    
    def send_newsletter(self, subject: str, content: str, recipients: List[str]) -> None:
        """Sends the newsletter to specified recipients."""
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