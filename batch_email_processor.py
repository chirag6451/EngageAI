import os
import logging
from datetime import datetime
from typing import List, Dict
from database import Database
from word_generator import WordGenerator
from email_utility import send_email_with_attachment
from cold_email_generator import get_cold_email_to_business

logger = logging.getLogger(__name__)

class BatchEmailProcessor:
    def __init__(self):
        self.db = Database()
        self.word_generator = WordGenerator()

    def process_batch(self, file_id: int) -> str:
        """
        Process all emails for a given file ID and generate a Word document
        Returns the path to the generated document
        """
        try:
            # Get all company profiles for the file
            profiles = self.db.get_company_profiles(file_id)
            if not profiles:
                logger.error(f"No profiles found for file ID: {file_id}")
                return None

            # Get file details for naming
            file_details = self.db.get_file_details(file_id)
            if not file_details:
                # Use a default name if file details not found
                logger.warning(f"No file details found for ID: {file_id}, using default name")
                filename = f"batch_{file_id}"
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

            # Process each profile and add to Word document
            for profile in profiles:
                company_name = profile['company_name']
                email_content = profile['profile_text']
                
                if email_content:
                    self.word_generator.add_email(company_name, email_content)
                    logger.info(f"Added email for company: {company_name}")
                else:
                    logger.warning(f"No email content for company: {company_name}")

            # Save the document
            saved_path = self.word_generator.save(output_path)
            if not saved_path:
                logger.error("Failed to save Word document")
                return None

            logger.info(f"Successfully generated Word document: {saved_path}")
            return saved_path

        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            return None

    def send_batch_document(self, document_path: str, recipient_email: str) -> bool:
        """
        Send the generated Word document as an email attachment
        """
        try:
            # Prepare email content
            subject = "Generated Cold Emails Batch"
            body = """
            Please find attached the generated cold emails document.
            
            This document contains all the generated cold emails in a formatted Word document.
            Each email includes the company name and the personalized email content.
            
            Best regards,
            Marketing Automation System
            """

            # Send email with attachment
            success = send_email_with_attachment(
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                attachment_path=document_path
            )

            if success:
                logger.info(f"Successfully sent batch document to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send batch document to {recipient_email}")
                return False

        except Exception as e:
            logger.error(f"Error sending batch document: {str(e)}")
            return False
