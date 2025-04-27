"""Configuration settings for personal and company information."""

# Personal Information
MY_NAME = "John Doe"
MY_DESIGNATION = "Marketing Director"
MY_COMPANY_NAME = "TechSolutions Inc."
MY_LINKEDIN = "https://www.linkedin.com/in/johndoe/"
MY_PHONE = "+1234567890"
MY_EMAIL = "john.doe@techsolutions.com"

MY_COMPANY_PROFILE = """
We specialize in AI-powered marketing solutions.

With 10 years of experience in digital marketing, our team of 25+ expert marketers excels in personalized outreach campaigns.

Our expertise spans:

Email Marketing – Personalized cold email campaigns with high conversion rates
Content Marketing – SEO-optimized content that drives organic traffic
Social Media Marketing – Engaging campaigns across all major platforms
Marketing Automation – Streamlined workflows for maximum efficiency
Analytics & Reporting – Data-driven insights to optimize your marketing ROI

We empower businesses with cutting-edge AI technology to reach their target audience effectively.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "john.doe@techsolutions.com"
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = "john.doe@techsolutions.com"
TO_EMAILS = ["recipient@company.com"]

# Database Configuration
DATABASE_NAME = "csv_manager.db"

# Crawling Configuration
MAX_RETRIES = 3
TIMEOUT = 30
