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

    def generate_newsletter_content(self, custom_content: str = "Thanks for signing up for the PCT Weekly Newsletter beta test! We would love to incorporate your feedback as much as possible so if you do, please reach out to Matthew at mhyan@bu.edu or Vincent at vinli@bu.edu or through slack.") -> Dict:
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
        
        # Updated CSS for styling the newsletter to match the provided image
        css = """
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f5f5f5;
            }
            
            .newsletter-container {
                max-width: 650px;
                margin: 0 auto;
                background-color: #fff;
                padding: 0;
                text-align: left;
                border-left: 1px solid #ddd;
                border-right: 1px solid #ddd;
            }
            
            .newsletter-header {
                background-image: url('https://whyphi-public.s3.us-east-1.amazonaws.com/newsletter_cover.jpg');
                background-size: cover;
                background-position: center;
                padding: 30px 20px 10px;
                text-align: center;
                height: 100px; /* Fixed height to ensure proper display */
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .newsletter-title {
                font-family: 'Times New Roman', Times, serif;
                font-size: 48px;
                font-weight: bold;
                color: #000;
                margin: 0;
                padding: 0;
                text-align: center;
            }
            
            .newsletter-subtitle {
                font-size: 20px;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-top: 1px solid #888;
                border-bottom: 1px solid #888;
                padding: 5px 0;
                margin: 10px 0 20px;
                text-align: center;
            }
            
            .welcome-message {
                padding: 20px;
                background-color: #fff;
                text-align: center;
            }
            
            .main-content {
                padding: 0 20px;
            }
            
            .section-banner {
                width: 100%;
                margin: 0 0 15px 0;
                overflow: hidden;
            }
            
            .section-banner img {
                width: 100%;
                display: block;
            }
            
            .job-opportunities-banner {
                width: 100%;
                margin: 20px 0 0 0;
                overflow: hidden;
            }
            
            .job-opportunities-banner img {
                width: 100%;
                display: block;
            }
            
            .job-sources {
                background-color: #f9f9f9;
                padding: 15px;
                margin: 0 0 20px 0;
                font-size: 14px;
                line-height: 1.5;
                border-bottom: 1px solid #eee;
            }
            
            .section-title {
                font-size: 28px;
                text-transform: uppercase;
                text-align: center;
                background-color: #f2f2f2;
                padding: 15px;
                margin: 0 0 20px;
                border: none;
            }
            
            .jobs-section {
                margin-bottom: 40px;
            }
            
            .job-item {
                margin-bottom: 20px;
                padding: 0 0 15px 0;
                border-bottom: 1px dotted #ddd;
            }
            
            .job-title {
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .job-details {
                font-size: 14px;
            }
            
            .events-section {
                margin-bottom: 40px;
            }
            
            .footer {
                text-align: center;
                padding: 20px;
                border-top: 1px solid #ddd;
            }
            
            .social-links {
                text-align: center;
                margin: 20px 0;
            }
            
            .social-links a {
                margin: 0 10px;
                text-decoration: none;
            }
        </style>
        """
        
        # Job sources text
        job_sources_html = """
        <div class="job-sources">
            <p>All jobs listed are within 7 days of being posted. They are being posted from these job repositories:</p>
            <p>Tech:
            <a href="https://github.com/SimplifyJobs/Summer2025-Internships" target="_blank">SimplifyJobs</a> 
            and <a href="https://github.com/cvrve/Summer2025-Internships" target="_blank">Cvrve</a></p>
            <p>Finance:
            <a href="https://docs.google.com/spreadsheets/d/15za1luZR08YmmBIFOAk6-GJB3T22StEuiZgFFuJeKW0/" target="_blank">RecruitU</a></p>
            <p>Consulting:
            <a href="https://github.com/jobright-ai/2025-Consultant-Internship" target="_blank">Jobright-ai</a></p>
            <p>Marketing:
            <a href="https://github.com/jobright-ai/2025-Marketing-Internship" target="_blank">Jobright-ai</a></p>
            <p>Please check these repositories often as they usually update daily. Best of luck with your job search!</p>
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