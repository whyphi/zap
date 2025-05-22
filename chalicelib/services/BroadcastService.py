from chalicelib.modules.ses import ses, SesDestination
from chalicelib.services.JobPostingService import job_posting_service
from chalicelib.utils import get_newsletter_css
from typing import List, Dict

# Job sources constant for better maintainability
JOB_SOURCE_LIST = {
    "Tech": [
        {
            "name": "SimplifyJobs", 
            "link": "https://github.com/SimplifyJobs/Summer2025-Internships/blob/dev/README.md", 
            "display_link": "https://github.com/SimplifyJobs/Summer2025-Internships"
         },
        {
            "name": "Cvrve", 
            "link": "https://github.com/cvrve/Summer2025-Internships/blob/dev/README.md", 
            "display_link": "https://github.com/cvrve/Summer2025-Internships"
         }
    ],
    "Finance": [
        {
            "name": "RecruitU", 
            "link": "https://docs.google.com/spreadsheets/d/15za1luZR08YmmBIFOAk6-GJB3T22StEuiZgFFuJeKW0/", 
            "display_link": "https://docs.google.com/spreadsheets/d/15za1luZR08YmmBIFOAk6-GJB3T22StEuiZgFFuJeKW0/"}
    ],
    "Consulting": [
        {
            "name": "Jobright-ai", 
            "link": "https://github.com/jobright-ai/2025-Consultant-Internship/blob/master/README.md", 
            "display_link": "https://github.com/jobright-ai/2025-Consultant-Internship"
         }
    ],
    "Marketing": [
        {
            "name": "Jobright-ai", 
            "link": "https://github.com/jobright-ai/2025-Marketing-Internship/blob/master/README.md", 
            "display_link": "https://github.com/jobright-ai/2025-Marketing-Internship"
         }
    ]
}

class BroadcastService:
    def __init__(self):
        self.ps = job_posting_service
    
    def generate_section_html(self, section_title: str, jobs: List[Dict]) -> str:
        """
        Generates an HTML section for a given list of jobs.
        """
        # Banner image URLs based on section title
        banner_urls = {
            "Finance": "https://whyphi-public.s3.us-east-1.amazonaws.com/finance_opportunities.jpg",
            "Tech": "https://whyphi-public.s3.us-east-1.amazonaws.com/tech_opportunities.jpg",
            "Consulting": "https://whyphi-public.s3.us-east-1.amazonaws.com/consulting_opportunities.jpg",
            "Marketing": "https://whyphi-public.s3.us-east-1.amazonaws.com/marketing_opportunities.jpg"
        }
        
        banner_url = banner_urls.get(section_title, "")
        banner_html = f'<div class="section-banner"><img src="{banner_url}" alt="{section_title} Banner" /></div>' if banner_url else ""
        
        html = f"""
        <div class='jobs-section'>
            {banner_html}
        """
        
        for job in jobs:
            company = job.get("company", "N/A")
            role = job.get("role", "N/A")
            link = job.get("link", "#")
            deadline = job.get("date", "N/A")
            
            # Use "Deadline" for Finance jobs and "Posted" for all other job types
            date_label = "Deadline" if section_title == "Finance" else "Posted"
            
            html += f"""
            <div class='job-item'>
                <div class='job-title'>{company} | {role}</div>
                <div class='job-details'>
                    <a href='{link}' target='_blank'>Apply</a> | {date_label}: {deadline}
                </div>
            </div>
            """
        
        html += "</div>"
        return html

    def generate_newsletter_content(self, custom_content: str = "Thanks for signing up for the PCT Weekly Newsletter beta test! We would love to incorporate your feedback as much as possible so if you do, please fill out this form: https://forms.gle/nW8cJPzXvHnyfkzV9 or reach out to Matthew and Vincent at mhyan@bu.edu and vinli@bu.edu or through slack.\nBest of luck with finals this week!") -> Dict:
        """
        Generates a complete newsletter with four sections:
            - Finance: Data from Google Sheets
            - Tech: Jobs from SimplifyJobs and cvrve GitHub repos
            - Consulting: Jobs from jobright-ai Consultant GitHub repo
            - Marketing: Jobs from jobright-ai Marketing GitHub repo
        
        Returns:
            Dict: A dictionary with HTML content and the raw job data.
        """
        # Finance jobs from RecruitU Google Sheets
        finance_jobs = self.ps.get_finance_jobs()
        
        # Fetch jobs from sources defined in JOB_SOURCE_LIST
        tech_jobs = []
        for source in JOB_SOURCE_LIST["Tech"]:
            tech_jobs += self.ps.get_jobs(source["link"])
            print(f"Fetched {len(tech_jobs)} jobs from {source['name']}")
        
        consulting_jobs = []
        for source in JOB_SOURCE_LIST["Consulting"]:
            consulting_jobs += self.ps.get_jobs(source["link"])
        
        marketing_jobs = []
        for source in JOB_SOURCE_LIST["Marketing"]:
            marketing_jobs += self.ps.get_jobs(source["link"])
        
        # Generate HTML for each section
        finance_section = self.generate_section_html("Finance", finance_jobs)
        tech_section = self.generate_section_html("Tech", tech_jobs)
        consulting_section = self.generate_section_html("Consulting", consulting_jobs)
        marketing_section = self.generate_section_html("Marketing", marketing_jobs)
        
        # Get CSS from utils function
        css = get_newsletter_css()
        
        # Generate job sources HTML dynamically from JOB_SOURCE_LIST
        job_sources_html = """
        <div class="job-sources">
            <p>All jobs listed have been posted within the last 7 days from these repositories:</p>
        """
        
        for category, sources in JOB_SOURCE_LIST.items():
            job_sources_html += f"<p>{category}: "
            links = []
            for i, source in enumerate(sources):
                links.append(f'<a href="{source["display_link"]}" target="_blank">{source["name"]}</a>')
            
            job_sources_html += " and ".join(links) + "</p>"
        
        job_sources_html += """
            <p>These repositories are updated daily, so please check them often. Best of luck with your job search!</p>
        </div>
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {css}
        </head>
        <body>
            <div class="newsletter-container">
                <div class="newsletter-header">
                </div>
                
                <div class="welcome-message">
                    <h2>Welcome to PCT's Weekly Newsletter</h2>
                    {custom_content}
                </div>
                
                <div class="main-content">
                    <div class="job-opportunities-banner">
                        <img src="https://whyphi-public.s3.us-east-1.amazonaws.com/job_opportunities.jpg" alt="Job Opportunities" />
                    </div>
                    
                    {job_sources_html}
                    
                    {tech_section}
                    {finance_section}
                    {marketing_section}
                    {consulting_section}
                    
                    <div class="events-section">
                        <h2 class="section-title">Events</h2>
                        <!-- Events content can be added here -->
                    </div>
                </div>
                
                <div class="footer">
                    <div class="social-links">
                        <a href="#" target="_blank">🔗</a>
                        <a href="#" target="_blank">📷</a>
                        <a href="#" target="_blank">📱</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
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