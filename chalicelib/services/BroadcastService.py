from chalicelib.modules.ses import ses, SesDestination
from chalicelib.services.JobPostingService import job_posting_service
from typing import List, Dict

class BroadcastService:
    def __init__(self):
        self.ps = job_posting_service
        # Map each section to its SVG image URL.
        # Update the URLs/paths as needed.
        self.svg_mapping = {
            "Finance": "https://whyphi-public.s3.us-east-1.amazonaws.com/finance_opportunities.jpg",
            "Tech": "https://whyphi-public.s3.us-east-1.amazonaws.com/tech_opportunities.jpg",
            "Consulting": "https://whyphi-public.s3.us-east-1.amazonaws.com/consulting_opportunities.jpg",
            "Marketing": "https://whyphi-public.s3.us-east-1.amazonaws.com/marketing_opportunities.jpg",
        }
        # Header and footer SVGs.
        self.header_svg = "https://whyphi-public.s3.us-east-1.amazonaws.com/newsletter_cover.jpg"
        self.footer_svg = "https://whyphi-public.s3.us-east-1.amazonaws.com/job_opportunities.jpg"

    def generate_section_html(self, section_title: str, jobs: List[Dict]) -> str:
        """
        Generates an HTML section for a given list of jobs.
        Each section includes an icon from the corresponding SVG.
        """
        # Retrieve the SVG for this section, if available.
        svg_img = self.svg_mapping.get(section_title, "")
        image_html = (
            f"<img src='{svg_img}' alt='{section_title} icon' class='section-icon'>"
            if svg_img else ""
        )
        html = (
            f"<div class='jobs-section'>"
            f"<div class='section-header'>{image_html}<h2>{section_title} Opportunities</h2></div>"
            f"<ul class='job-list'>"
        )
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
        
        # CSS updated to style the newsletter with header, footer, and section icons.
        css = """
        <style>
            .newsletter {
                font-family: 'Helvetica', Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                color: #333;
            }
            .newsletter-header, .newsletter-footer {
                text-align: center;
                margin: 20px 0;
            }
            .newsletter-header img, .newsletter-footer img {
                max-width: 100%;
            }
            .jobs-section {
                margin: 15px 0;
                padding: 15px;
                background-color: #fff;
                border-bottom: 1px solid #eee;
            }
            .section-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 10px;
            }
            .section-header h2 {
                margin: 0;
                font-size: 18px;
                font-weight: 500;
            }
            .job-list {
                list-style-type: none;
                padding-left: 0;
            }
            .job-item {
                margin-bottom: 10px;
                padding: 8px 0;
                border-left: 2px solid #ddd;
                padding-left: 10px;
            }
            .custom-content {
                margin-bottom: 20px;
            }
        </style>
        """
        
        full_html = f"""
        {css}
        <div class="newsletter">
            <div class="newsletter-header">
                <img src="{self.header_svg}" alt="Newsletter Header">
            </div>
            <div class="custom-content">
                {custom_content}
            </div>
            {finance_section}
            {tech_section}
            {consulting_section}
            {marketing_section}
            <div class="newsletter-footer">
                <img src="{self.footer_svg}" alt="Newsletter Footer">
            </div>
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