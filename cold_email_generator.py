import os
import json
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from pydantic import BaseModel
import openai
from temp_config import OPENAI_API_KEY
from crawl_with_ai import fetch_from_url
from ai_profile_generator import AIProfileGenerator
from get_weather import get_weather_forecast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize AI Profile Generator
profile_generator = AIProfileGenerator()

# Constants
SYSTEM_PROMPT = """You are a professional cold email writer who creates highly personalized and engaging emails. 
When weather information is provided, use it to create a personalized opening that references the weather at the RECIPIENT'S location, not yours.
For example, if given weather data for Dubai showing sunny conditions, you might say "I hope you're staying cool in Dubai's sunny weather" rather than talking about your own weather.
Focus on making the weather reference feel natural and relevant to the business context where possible.
Always maintain a professional tone while being personable."""

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

def truncate_text(text: str, max_length: int = 300) -> str:
    """Truncate text to max_length while preserving complete sentences"""
    if not text or len(text) <= max_length:
        return text
    
    # Find the last complete sentence within the limit
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_exclamation = truncated.rfind('!')
    last_question = truncated.rfind('?')
    
    # Find the last sentence ending punctuation
    last_sentence_end = max(last_period, last_exclamation, last_question)
    
    if last_sentence_end > 0:
        return text[:last_sentence_end + 1].strip()
    
    # If no sentence ending found, truncate at the last space
    last_space = truncated.rfind(' ')
    if last_space > 0:
        return text[:last_space].strip() + '...'
    
    return truncated.strip() + '...'

def get_cold_email_prompt(
    company_profile: str,
    business_name: str,
    company_website: str,
    location: str = None,
    config: dict = None
) -> str:
    """Generate a prompt for the cold email."""
    weather_context = ""
    
    if not config:
        raise ValueError("Config is required for email generation")
    
    if location:
        try:
            logger.info(f"Getting weather data for location: {location}")
            weather_data = get_weather_forecast(location)
            if weather_data:
                weather_context = f"""
Weather Information:
Location: {location}
Current Weather: {weather_data}

Use this weather information to create a natural, personalized opening that references the weather at their location.
"""
                logger.info(f"Weather context added to prompt: {weather_context}")
        except Exception as e:
            logger.error(f"Error getting weather data: {str(e)}")
    
    prompt = f"""{SYSTEM_PROMPT}

Task: Write a personalized cold email to {business_name} ({company_website}).

{weather_context}
Company Information:
{company_profile}

My Information:
- Name: {config['MY_NAME']}
- Role: {config['MY_DESIGNATION']}
- Company: {config['MY_COMPANY_NAME']}
- Experience: {config['MY_COMPANY_PROFILE']}
- Contact: {config['MY_LINKEDIN']} | {config['MY_PHONE']} | {config['MY_EMAIL']}

Guidelines:
1. Start with a personalized opening that mentions their location's weather if available
2. Focus on their business needs and how we can help
3. Keep the tone professional yet friendly
4. Include my contact information in a signature block
5. Format the email with proper spacing and structure
"""

    logger.info(f"\n=== Final Prompt Weather Context ===\n{weather_context}")
    return prompt

def get_cold_email_to_business(
    company_profile: str,
    business_name: str,
    company_website: str,
    company_data: dict = None,
    config: dict = None
) -> str:
    """Generate a cold email for a business."""
    try:
        logger.info("\n=== Generating Cold Email ===")
        
        # Extract location from company_data
        location = None
        if company_data and 'file_data' in company_data:
            file_data = company_data['file_data']
            location = file_data.get('Location')
            logger.info(f"Location from file_data: {location}")

        logger.info(f"Location passed to get_cold_email_to_business: {location}")
        
        logger.info("\n=== Cold Email Generation Data ===")
        logger.info(f"Business Name: {business_name}")
        logger.info(f"Website: {company_website}")
        logger.info(f"Location: {location}")
        
        # Truncate company profile if needed
        original_length = len(company_profile)
        company_profile = truncate_text(company_profile)
        truncated_length = len(company_profile)
        
        logger.info(f"Original Profile Length: {original_length}")
        logger.info(f"Truncated Profile Length: {truncated_length}")
        
        # Get weather data if location is available
        weather_context = ""
        if location:
            logger.info(f"Getting weather data for location: {location}")
            weather_data = get_weather_forecast(location)
            if weather_data:
                logger.info(f"Weather data received: {weather_data}")
                weather_context = f"\nWeather Context: {weather_data}\n"
            else:
                logger.warning(f"No weather data received for location: {location}")
        
        logger.info("\n=== Final Prompt Weather Context ===")
        logger.info(weather_context if weather_context else "No weather context available")
        
        # Generate the prompt with weather context if available and config
        prompt = get_cold_email_prompt(
            company_profile=company_profile,
            business_name=business_name,
            company_website=company_website,
            location=location,
            config=config
        )
        
        logger.info(f"Prompt generated with weather context? {bool(weather_context)}")
        
        # Generate the email using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 to avoid rate limits
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        email_content = response.choices[0].message.content.strip()
        logger.info(f"Generated email includes weather reference? {'weather' in email_content.lower()}")
        
        return email_content

    except Exception as e:
        logger.error(f"Error generating cold email: {str(e)}")
        return None

def generate_company_profile(company_data: dict) -> Optional[Dict]:
    """Generate a company profile and cold email based on the provided data."""
    try:
        logger.info(f"\n=== Starting Company Profile Generation ===")
        logger.info(f"Raw Company Data: {company_data}")
        
        # Initialize location
        location = None
        
        # First try to get location from file_data
        if 'file_data' in company_data:
            logger.info("Found file_data in company_data")
            try:
                file_data = company_data['file_data']
                logger.info(f"File data type: {type(file_data)}")
                logger.info(f"File data content: {file_data}")
                
                if isinstance(file_data, str):
                    try:
                        file_data = json.loads(file_data)
                        logger.info("Successfully parsed file_data JSON")
                    except json.JSONDecodeError:
                        logger.info("file_data is a string but not JSON")
                
                if isinstance(file_data, dict):
                    location = file_data.get('Location')
                    logger.info(f"Location from file_data: {location}")
                    
                    if not location and 'row_data' in file_data:
                        row_data = file_data['row_data']
                        logger.info(f"Found row_data in file_data: {row_data}")
                        
                        if isinstance(row_data, str):
                            try:
                                row_data = json.loads(row_data)
                                logger.info("Successfully parsed row_data JSON")
                            except json.JSONDecodeError:
                                logger.info("row_data is a string but not JSON")
                        
                        if isinstance(row_data, dict):
                            location = row_data.get('Location')
                            logger.info(f"Location from row_data in file_data: {location}")
            except Exception as e:
                logger.error(f"Error processing file_data: {str(e)}")
                logger.debug(f"Problematic file_data: {company_data.get('file_data')}")
        
        # If still no location, try direct row_data
        if not location and 'row_data' in company_data:
            logger.info("Checking direct row_data")
            try:
                row_data = company_data['row_data']
                logger.info(f"Direct row_data type: {type(row_data)}")
                logger.info(f"Direct row_data content: {row_data}")
                
                if isinstance(row_data, str):
                    try:
                        row_data = json.loads(row_data)
                        logger.info("Successfully parsed direct row_data JSON")
                    except json.JSONDecodeError:
                        logger.info("direct row_data is a string but not JSON")
                
                if isinstance(row_data, dict):
                    location = row_data.get('Location')
                    logger.info(f"Location from direct row_data: {location}")
            except Exception as e:
                logger.error(f"Error processing direct row_data: {str(e)}")
        
        # If still no location, try alternative fields
        if not location:
            logger.info("Checking alternative location fields...")
            location_fields = ['location', 'city', 'address', 'headquarters', 'hq']
            data_sources = [company_data]
            
            if 'file_data' in company_data:
                if isinstance(company_data['file_data'], dict):
                    data_sources.append(company_data['file_data'])
                elif isinstance(company_data['file_data'], str):
                    try:
                        data_sources.append(json.loads(company_data['file_data']))
                    except json.JSONDecodeError:
                        pass
            
            for source in data_sources:
                for field in location_fields:
                    if field in source and source[field]:
                        location = source[field]
                        logger.info(f"Found location in '{field}' field: {location}")
                        break
                if location:
                    break

        if not location:
            logger.warning("No location found in any fields")
        else:
            logger.info(f"Final location value: {location}")
        
        # Get company profile
        logger.info(f"Processing company: {company_data.get('company_name')}")
        company_profile = crawl_and_generate_profile(company_data)
        if not company_profile:
            logger.error("Failed to generate company profile")
            return None

        # Get weather data if location is available
        weather_context = ""
        if location:
            logger.info(f"Getting weather data for location: {location}")
            weather_data = get_weather_forecast(location)
            if weather_data:
                logger.info(f"Weather data received: {weather_data}")
                weather_context = f"\nWeather Context: {weather_data}\n"
            else:
                logger.warning(f"No weather data received for location: {location}")

        # Generate cold email
        logger.info(f"Generating cold email with location: {location}")
        cold_email = get_cold_email_to_business(
            company_profile=company_profile.get('company_description', ''),
            business_name=company_data.get('company_name', ''),
            company_website=company_data.get('website', ''),
            company_data=company_data
        )

        if not cold_email:
            logger.error("Failed to generate cold email")
            return None

        return {
            'company_name': company_data.get('company_name', ''),
            'profile_text': cold_email,
            'source_file_id': company_data.get('file_id'),
            'status': 'success'
        }

    except Exception as e:
        logger.error(f"Error in generate_company_profile: {str(e)}")
        logger.exception("Full traceback:")
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
            company_data['company_description'] = truncate_text(profile_result['profile'], 300)
        else:
            logger.error(f"Failed to generate profile: {profile_result.get('error', 'Unknown error')}")
        
        return company_data
    except Exception as e:
        logger.error(f"Error in crawl_and_generate_profile: {str(e)}")
        return company_data

def generate_multiple_profiles(companies_data: List[dict]) -> List[dict]:
    """Generate cold emails for multiple companies"""
    profiles = []
    for company_data in companies_data:
        profile = generate_company_profile(company_data)
        profiles.append(profile)
    return profiles
