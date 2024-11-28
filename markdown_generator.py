import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    def __init__(self):
        self.markdown_template = """
# Generated Cold Emails
*Generated on: {timestamp}*

---
{email_content}
"""

        self.email_template = """
## Email for {company_name}

{content}

---
"""

    def generate_markdown(self, emails, output_path='generated_emails.md'):
        """Generate Markdown file with formatted emails"""
        try:
            # Generate email content
            email_sections = []
            for company_name, email_text in emails:
                email_section = self.email_template.format(
                    company_name=company_name,
                    content=email_text
                )
                email_sections.append(email_section)

            # Combine all content
            full_content = self.markdown_template.format(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email_content='\n'.join(email_sections)
            )
            
            # Save the Markdown file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Successfully generated Markdown file at {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating Markdown file: {str(e)}")
            return None
