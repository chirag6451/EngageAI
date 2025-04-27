import os
import time
import logging
from datetime import datetime
from typing import List, Dict
from database import Database
from word_generator import WordGenerator
from email_utility import send_email_with_attachment

logger = logging.getLogger(__name__)

class BatchEmailProcessor:
    def __init__(self):
        self.db = Database()
        self.word_generator = WordGenerator()

    def process_batch(self, file_id: int, delay_seconds: int = 5) -> Dict:
        """
        Process all emails for a given file ID and generate a Word document
        Returns a dictionary with the results
        """
        results = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'details': []
        }

        try:
            # Get all company profiles for the file
            profiles = self.db.get_company_profiles(file_id)
            if not profiles:
                logger.error(f"No profiles found for file ID: {file_id}")
                return results

            # Get file details for naming
            file_details = self.db.get_file_details(file_id)
            if not file_details:
                logger.warning(f"No file details found for ID: {file_id}, using default name")
                filename = f"engageai_batch_{file_id}"
            else:
                filename = os.path.splitext(file_details[1])[0]
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), 'generated_emails')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                output_dir, 
                f"{filename}_emails_{timestamp}.docx"
            )

            # Generate Word document with all emails
            self.word_generator.generate_document(profiles, output_path)
            
            results['total'] = len(profiles)
            
            # Process each profile and send emails
            for profile in profiles:
                company_name = profile.get('company_name', 'Unknown Company')
                company_email = profile.get('email')
                
                if not company_email:
                    logger.warning(f"No email found for {company_name}")
                    results['failed'] += 1
                    results['details'].append({
                        'company': company_name,
                        'status': 'failed',
                        'reason': 'No email address found'
                    })
                    continue
                
                # Send email with attachment
                success = send_email_with_attachment(
                    to_email=company_email,
                    subject=f"Partnership Opportunity with {company_name}",
                    content=profile.get('email_content', ''),
                    attachment_path=output_path
                )
                
                if success:
                    results['sent'] += 1
                    results['details'].append({
                        'company': company_name,
                        'email': company_email,
                        'status': 'sent'
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'company': company_name,
                        'email': company_email,
                        'status': 'failed',
                        'reason': 'Failed to send email'
                    })
                
                # Add delay between emails
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
            
            return results

        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            return results
