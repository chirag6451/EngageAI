import os
import openai
from typing import Dict, List

class AIProfileGenerator:
    def __init__(self):
        # Initialize OpenAI client
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key

    def generate_company_profile(self, company_data: Dict) -> Dict:
        """
        Generate a company profile using OpenAI based on crawled data
        
        Args:
            company_data: Dictionary containing company info and HTML content
            
        Returns:
            Dictionary containing the generated profile
        """
        prompt = self._create_prompt(company_data)
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional business analyst. Create a detailed company profile based on the provided information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                'company_name': company_data['company_name'],
                'profile': response.choices[0].message.content,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'company_name': company_data['company_name'],
                'profile': None,
                'status': 'error',
                'error': str(e)
            }

    def _create_prompt(self, company_data: Dict) -> str:
        """
        Create a prompt for OpenAI based on company data
        """
        prompt = f"""
        Create a detailed company profile based on the following information:
        
        Company Name: {company_data['company_name']}
        Founded Date: {company_data.get('funded_date', 'Not available')}
        
        Website Content:
        {company_data.get('html_content', 'No content available')}
        
        Please include the following sections in your analysis:
        1. Company Overview
        2. Products/Services
        3. Target Market
        4. Key Features/Differentiators
        5. Business Model
        6. Market Position
        
        Focus on extracting factual information from the provided content.
        """
        return prompt

    def generate_multiple_profiles(self, companies_data: List[Dict]) -> List[Dict]:
        """
        Generate profiles for multiple companies
        """
        profiles = []
        for company_data in companies_data:
            profile = self.generate_company_profile(company_data)
            profiles.append(profile)
        return profiles
