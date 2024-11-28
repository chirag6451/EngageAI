import os
import json
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from pydantic import BaseModel
import openai
from config import (
    MY_NAME, MY_DESIGNATION, MY_COMPANY_NAME, MY_COMPANY_PROFILE,
    MY_LINKEDIN, MY_PHONE, MY_EMAIL, OPENAI_API_KEY
)
from crawl_with_ai import fetch_from_url
from ai_profile_generator import AIProfileGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize AI Profile Generator
profile_generator = AIProfileGenerator()

class ColdEmailToBusiness(BaseModel):
    cold_email: str

def extract_company_info(html_content: str) -> Dict[str, str]:
    """Extract relevant information from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    info = {}
    
    # Try to extract company description
    description_tags = soup.find_all(['p', 'div'], class_=['description', 'about', 'about-us', 'company-description'])
    if description_tags:
        info['description'] = ' '.join([tag.get_text().strip() for tag in description_tags[:2]])
    else:
        # Fallback to first few paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            info['description'] = ' '.join([p.get_text().strip() for p in paragraphs[:2]])
    
    # Try to extract products/services
    product_tags = soup.find_all(['div', 'section'], class_=['products', 'services', 'solutions'])
    if product_tags:
        products = []
        for tag in product_tags[:3]:  # Limit to first 3 product sections
            product_text = tag.get_text().strip()
            if product_text:
                products.append(product_text)
        if products:
            info['products_services'] = ' '.join(products)
    
    # Try to extract technologies/expertise
    tech_tags = soup.find_all(['div', 'section'], class_=['technologies', 'expertise', 'tech-stack'])
    if tech_tags:
        techs = []
        for tag in tech_tags[:2]:
            tech_text = tag.get_text().strip()
            if tech_text:
                techs.append(tech_text)
        if techs:
            info['technologies'] = ' '.join(techs)
    
    return {k: v for k, v in info.items() if v}  # Only return non-empty values

def get_cold_email_prompt(company_profile: str, business_name: str, company_website: str) -> str:
    """Generate the prompt for cold email generation"""
    return f"""You are a professional cold email writer. Write a personalized cold email to {business_name} ({company_website}).

Here is information about my business:
- My name: {MY_NAME}
- My role: {MY_DESIGNATION}
- My company: {MY_COMPANY_NAME}
- Company profile: {MY_COMPANY_PROFILE}
- My LinkedIn: {MY_LINKEDIN}
- My phone: {MY_PHONE}
- My email: {MY_EMAIL}

Here is the information about the target company:
{company_profile}

Important instructions:
1. DO NOT use ANY placeholder text like "[Your Company]", "[Name]", etc. If you don't have specific information, craft the email without mentioning it rather than using placeholders.
2. Write a highly personalized email based on the company information provided. If certain information is missing, write naturally without it rather than making assumptions.
3. Keep the email concise, professional, and focused on value proposition.
4. Use a natural, conversational tone while maintaining professionalism.
5. Include my contact information and company details from the provided config, not as placeholders.
6. Focus on how {MY_COMPANY_NAME} can specifically help {business_name} based on their business context.
7. End with a clear but non-aggressive call to action.
8. Format the email in markdown.
9. Use EXACTLY this signature format at the end (no other signatures or contact information in the email):

---

Best regards,
{MY_NAME}
{MY_DESIGNATION}
{MY_COMPANY_NAME}

[LinkedIn]({MY_LINKEDIN}) | [Phone: {MY_PHONE}](tel:{MY_PHONE.replace(' ', '')}) | [Email: {MY_EMAIL}](mailto:{MY_EMAIL})

Write only the email content with the exact signature format above, no additional explanations or notes."""

def get_cold_email_to_business(
    company_profile: str,
    founder_name: str = "",
    business_name: str = "",
    company_website: str = "",
    company_linkedin: str = "",
    company_email: str = "",
    company_phone: str = "",
    company_location: str = ""
):
    """
    Generate a cold email using the OpenAI API
    """
    try:
        # Extract information from HTML
        company_info = extract_company_info(company_profile)
        
        # Build the prompt with available information
        prompt = get_cold_email_prompt(company_profile, business_name, company_website)
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional business development expert crafting personalized cold emails. Only use information explicitly provided, never make assumptions or add placeholder text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Extract the generated email
        if response.choices and response.choices[0].message:
            email = response.choices[0].message.content
            
            # Add signature
            email += f"\n\nBest regards,\n{MY_NAME}\n{MY_DESIGNATION}\n{MY_COMPANY_NAME}\nLinkedIn: {MY_LINKEDIN}\nPhone: {MY_PHONE}\nEmail: {MY_EMAIL}"
            
            return email
        else:
            logger.error("No response generated from OpenAI API")
            return None

    except Exception as e:
        logger.error(f"Error generating cold email: {str(e)}")
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
