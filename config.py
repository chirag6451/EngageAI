"""Configuration settings for personal and company information."""

# Personal Information
MY_NAME = "Jaimin Parmar"  # Replace with your actual name
MY_DESIGNATION = "Business Development Manager"  # Replace with your designation
MY_COMPANY_NAME = "IndaPoint Technologies Private LImited"  # Replace with your company name
MY_LINKEDIN = "https://www.linkedin.com/in/chiragahmedabadi/"  # Replace with your LinkedIn profile
MY_PHONE = "+91 9408707113"  # Replace with your phone number
MY_EMAIL = "info@indapoint.com"  # Replace with your email

MY_COMPANY_PROFILE = """
We specialize in cutting-edge AI-based solutions, leveraging the latest advancements in Generative AI, Retrieval-Augmented Generation (RAG), fine-tuning, and Large Language Models (LLMs) such as OpenAI, Claude, Mistral, DeepSeek, and others.

With 18 years of experience in software development, web development, and mobile app development, our team of 50+ expert developers excels in crafting AI-driven applications tailored for diverse industries.

Our expertise spans:

Generative AI – Custom AI applications powered by LLMs for text, image, and multimodal generation.
Retrieval-Augmented Generation (RAG) – Enhanced AI responses through optimized retrieval and knowledge integration.
LLM Fine-Tuning & Customization – Adapting models to specific business needs for superior accuracy and performance.
Machine Learning & Deep Learning – Developing robust AI systems using state-of-the-art architectures.
Reinforcement Learning – AI models capable of adaptive learning and decision-making.
We empower businesses with AI-driven automation, intelligent assistants, and cutting-edge machine learning models, delivering high-performance solutions tailored to industry-specific challenges.
"""  # Replace with your actual company profile

import os

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'email-smtp.ap-south-1.amazonaws.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'info@indapoint.com')
TO_EMAILS = os.getenv('TO_EMAILS', 'chirag@indapoint.com').split(',')

# Database Configuration
DATABASE_NAME = "csv_manager.db"

# Crawling Configuration
MAX_RETRIES = 3
TIMEOUT = 30
