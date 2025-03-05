"""Configuration settings for personal and company information."""

# Personal Information
MY_NAME = "Your Name"  # Replace with your actual name
MY_DESIGNATION = "Your Designation"  # Replace with your designation
MY_COMPANY_NAME = "Your Company Name"  # Replace with your company name
MY_LINKEDIN = "https://www.linkedin.com/in/yourprofile/"  # Replace with your LinkedIn profile
MY_PHONE = "+1234567890"  # Replace with your phone number
MY_EMAIL = "your.email@company.com"  # Replace with your email

MY_COMPANY_PROFILE = """
We specialize in [Your Company's Specialization].

With [X] years of experience in [Industry/Field], our team of [Y]+ expert [professionals] excels in [Key Services].

Our expertise spans:

[Expertise 1] – [Description]
[Expertise 2] – [Description]
[Expertise 3] – [Description]
[Expertise 4] – [Description]
[Expertise 5] – [Description]

We empower businesses with [Your Value Proposition].
"""  # Replace with your actual company profile

import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Email Configuration
SMTP_SERVER = "your.smtp.server"  # Replace with your SMTP server
SMTP_PORT = 587  # Replace with your SMTP port
SMTP_USER = "your_smtp_user"  # Replace with your SMTP username
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # Set this in .env file
FROM_EMAIL = "your.email@company.com"  # Replace with your email
TO_EMAILS = ["recipient@company.com"]  # Replace with recipient emails

# Database Configuration
DATABASE_NAME = "csv_manager.db"

# Crawling Configuration
MAX_RETRIES = 3
TIMEOUT = 30
