import os
from datetime import datetime
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class HTMLGenerator:
    def __init__(self):
        self.html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Generated Cold Emails</title>
    <style>
        body {
            font-family: 'Calibri', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 14px;
        }
        .email-container {
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        }
        .email-header {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .email-header h2 {
            color: #3498db;
            margin: 0;
            font-size: 20px;
        }
        .email-content {
            line-height: 1.6;
            color: #2c3e50;
            white-space: pre-wrap;
        }
        .separator {
            border-top: 1px solid #e0e0e0;
            margin: 30px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Generated Cold Emails</h1>
            <div class="timestamp">Generated on: {{ timestamp }}</div>
        </div>
        
        {% for email in emails %}
        <div class="email-container">
            <div class="email-header">
                <h2>Email for {{ email.company_name }}</h2>
            </div>
            <div class="email-content">
                {{ email.content }}
            </div>
        </div>
        {% if not loop.last %}
        <div class="separator"></div>
        {% endif %}
        {% endfor %}
    </div>
</body>
</html>
"""

    def generate_html(self, emails, output_path='generated_emails.html'):
        """Generate HTML file with formatted emails"""
        try:
            # Prepare the template
            template = Template(self.html_template)
            
            # Prepare the data
            email_data = [
                {
                    'company_name': company_name,
                    'content': email_text
                }
                for company_name, email_text in emails
            ]
            
            # Render the template
            html_content = template.render(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                emails=email_data
            )
            
            # Save the HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Successfully generated HTML file at {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating HTML file: {str(e)}")
            return None
