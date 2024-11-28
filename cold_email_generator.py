import os
import logging
from typing import Optional, List, Dict
from pydantic import BaseModel
from openai import OpenAI
from bs4 import BeautifulSoup
import re
from config import (
    MY_NAME, MY_DESIGNATION, MY_COMPANY_NAME, MY_COMPANY_PROFILE,
    MY_LINKEDIN, MY_PHONE, MY_EMAIL
)
from crawl_with_ai import fetch_from_url
from ai_profile_generator import AIProfileGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI()

# Initialize AI Profile Generator
profile_generator = AIProfileGenerator()

class ColdEmailToBusiness(BaseModel):
    cold_email: str

def extract_company_info_from_html(html_content: str) -> Dict[str, str]:
    """
    Extract relevant company information from HTML content
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize dictionary for company info
        company_info = {
            'description': '',
            'products_services': '',
            'features': '',
            'target_market': ''
        }
        
        # Get all text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Extract main content sections
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text(strip=True)]
        
        # Combine relevant sections
        company_info['description'] = ' '.join(paragraphs[:2]) if paragraphs else ''
        
        # Look for features or products sections
        features_section = False
        products_section = False
        features = []
        products = []
        
        for heading in headings:
            heading_lower = heading.lower()
            if 'feature' in heading_lower:
                features_section = True
                products_section = False
            elif 'product' in heading_lower or 'service' in heading_lower:
                products_section = True
                features_section = False
            
            if features_section:
                features.append(heading)
            elif products_section:
                products.append(heading)
        
        company_info['features'] = ' '.join(features)
        company_info['products_services'] = ' '.join(products)
        
        # Clean up and format the text
        for key in company_info:
            if company_info[key]:
                # Remove multiple spaces and newlines
                company_info[key] = re.sub(r'\s+', ' ', company_info[key]).strip()
                # Remove very short entries
                if len(company_info[key]) < 10:
                    company_info[key] = ''
        
        return company_info
    
    except Exception as e:
        logger.error(f"Error extracting company info from HTML: {str(e)}")
        return {
            'description': '',
            'products_services': '',
            'features': '',
            'target_market': ''
        }

def get_cold_email_to_business(
    company_profile: str,
    founder_name: str,
    business_name: str,
    company_website: str = None,
    company_linkedin: str = None,
    company_email: str = None,
    company_phone: str = None,
    company_location: str = None
):
    """
    Generate a cold email for a business based on their profile and contact information.
    """
    try:
        logger.info(f"Generating cold email for business: {business_name}")
        
        # Extract company information from HTML
        company_info = extract_company_info_from_html(company_profile)
        
        # Build company details section
        company_details = []
        if company_website:
            company_details.append(f"Website: {company_website}")
        if company_linkedin:
            company_details.append(f"LinkedIn: {company_linkedin}")
        if company_email:
            company_details.append(f"Email: {company_email}")
        if company_phone:
            company_details.append(f"Phone: {company_phone}")
        if company_location:
            company_details.append(f"Location: {company_location}")
        
        company_details_text = "\n".join(company_details) if company_details else "No additional contact details available"

        prompt = f"""You are an expert in writing cold emails to businesses. Create a highly personalized and compelling cold email based on the following information:

MY INFORMATION:
- Name: {MY_NAME}
- Designation: {MY_DESIGNATION}
- Company: {MY_COMPANY_NAME}
- LinkedIn: {MY_LINKEDIN}
- Phone: {MY_PHONE}
- Email: {MY_EMAIL}
- Company Profile: {MY_COMPANY_PROFILE}

TARGET COMPANY INFORMATION:
- Company Name: {business_name}
- Website: {company_website}
- Description: {company_info['description']}
- Products/Services: {company_info['products_services']}
- Key Features: {company_info['features']}

INSTRUCTIONS:
Create a highly personalized and creative cold email that:

1. FORMAT:
   - First line: Write an attention-grabbing subject line that mentions their company specifically
   - Second line: Blank
   - Main body: 3-4 concise, impactful paragraphs
   - Signature: Professional signature with all contact details

2. CONTENT REQUIREMENTS:
   - Start with a personalized greeting
   - Reference specific details about their products/services from the extracted information
   - Show understanding of their business value proposition
   - Very briefly explain our relevant expertise (1-2 sentences max)
   - Include a clear, specific call to action (e.g., "Would you be open to a 15-minute call this week?")
   - Keep the entire email under 200 words

3. TONE AND STYLE:
   - Professional yet conversational
   - Show genuine interest and enthusiasm
   - Focus on their business first, our offering second
   - Be specific and relevant to their industry
   - Avoid generic phrases and sales jargon

4. SIGNATURE FORMAT:
Best regards,
{MY_NAME}
{MY_DESIGNATION}
{MY_COMPANY_NAME}
LinkedIn: {MY_LINKEDIN}
Phone: {MY_PHONE}
Email: {MY_EMAIL}"""

        completion = client.beta.chat.completions.parse(
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {
                    "role": "system", 
                    "content": prompt
                },
            ],
            response_format=ColdEmailToBusiness,
        )
        message = completion.choices[0].message
        if message.content:
            logger.info("Successfully generated cold email")
            return message.content
        else:
            logger.error("Failed to generate cold email")
            return None
    except Exception as e:
        logger.error(f"An error occurred while generating cold email: {str(e)}")
        return None

def crawl_and_generate_profile(company_data: Dict) -> Dict:
    """
    Crawl company website and generate profile using AI
    """
    try:
        # Extract website URL
        website_url = company_data.get('website')
        if not website_url:
            logger.warning(f"No website URL provided for {company_data.get('company_name', 'Unknown Company')}")
            return company_data

        # Crawl website content
        logger.info(f"Crawling website: {website_url}")
        html_content = fetch_from_url(website_url)
        
        # Add HTML content to company data
        company_data['html_content'] = html_content
        
        # Generate profile using AI
        logger.info("Generating company profile using AI")
        profile_result = profile_generator.generate_company_profile(company_data)
        
        # Update company data with generated profile
        if profile_result['status'] == 'success':
            company_data['company_description'] = profile_result['profile']
        else:
            logger.error(f"Failed to generate profile: {profile_result.get('error', 'Unknown error')}")
        
        return company_data
    except Exception as e:
        logger.error(f"Error in crawl_and_generate_profile: {str(e)}")
        return company_data

def generate_company_profile(company_data: dict) -> Optional[dict]:
    """Generate a company profile and cold email based on the provided data."""
    try:
        # First crawl and generate profile if website is available
        company_data = crawl_and_generate_profile(company_data)

        # Extract all available information
        company_name = company_data.get('company_name', '')
        company_profile = company_data.get('company_description', '')
        founder_name = company_data.get('founder_name', 'the founder')
        company_website = company_data.get('website')
        company_linkedin = company_data.get('linkedin')
        company_email = company_data.get('email')
        company_phone = company_data.get('phone')
        company_location = company_data.get('location')

        # Generate cold email with all available information
        cold_email = get_cold_email_to_business(
            company_profile=company_profile,
            founder_name=founder_name,
            business_name=company_name,
            company_website=company_website,
            company_linkedin=company_linkedin,
            company_email=company_email,
            company_phone=company_phone,
            company_location=company_location
        )

        if cold_email:
            return {
                'company_name': company_name,
                'cold_email': cold_email,
                'status': 'success'
            }
        else:
            return {
                'company_name': company_name,
                'error_message': 'Failed to generate cold email',
                'status': 'error'
            }
    except Exception as e:
        logger.error(f"Error in generate_company_profile: {str(e)}")
        return {
            'company_name': company_data.get('company_name', ''),
            'error_message': str(e),
            'status': 'error'
        }

def generate_multiple_profiles(companies_data: List[dict]) -> List[dict]:
    """Generate cold emails for multiple companies"""
    profiles = []
    for company_data in companies_data:
        profile = generate_company_profile(company_data)
        profiles.append(profile)
    return profiles
