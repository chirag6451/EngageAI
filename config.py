"""Configuration settings for personal and company information."""

# Personal Information
MY_NAME = "Chirag Ahmedabadi"  # Replace with your actual name
MY_DESIGNATION = "Business Development Manager"  # Replace with your designation
MY_COMPANY_NAME = "IndaPoint Technologies Private LImited"  # Replace with your company name
MY_LINKEDIN = "https://www.linkedin.com/in/chiragahmedabadi/"  # Replace with your LinkedIn profile
MY_PHONE = "+91 9898989898"  # Replace with your phone number
MY_EMAIL = "chirag@indapoint.com"  # Replace with your email

MY_COMPANY_PROFILE = """
- We proivde AI based solutions
- Sotware development, Web development, Mobile app development and AI based solutions
- Expertise and experience with AI and machine learning
- 18 Years old company with team of 50+ developers
-Generative AI, Machine learning, Deep learning, Neural networks, Reinforcement learning, Mobile app development
"""  # Replace with your actual company profile

import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Email Configuration
SMTP_SERVER = "email-smtp.ap-south-1.amazonaws.com"
SMTP_PORT = 587
SMTP_USER = "AKIA2LDJTSEUO7GR3XK2"
SMTP_PASSWORD = "BEHQRNcFLgNoIjWFxBGMXzYFESjCsAIKRQeggf07CC1B"
FROM_EMAIL = "info@indapoint.com"
TO_EMAILS = ["chirag@indapoint.com"]

# Database Configuration
DATABASE_NAME = "csv_manager.db"

# Crawling Configuration
MAX_RETRIES = 3
TIMEOUT = 30
