import os
import csv
import json
import logging
from typing import List, Dict
from database import Database
from crawl_with_ai import fetch_from_url
from cold_email_generator import get_cold_email_to_business
from email_utility import send_email, format_email_content
from config import TO_EMAILS
from batch_email_processor import BatchEmailProcessor
from word_generator import WordGenerator
from html_generator import HTMLGenerator
from markdown_generator import MarkdownGenerator
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketingAutomation:
    def __init__(self):
        self.db = Database()

    def process_csv_file(self, file_path: str) -> int:
        """
        Process CSV file and import data into database
        Returns file_id if successful
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            logger.info(f"Opening CSV file: {file_path}")
            # Read CSV file
            with open(file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                columns = csv_reader.fieldnames
                logger.info(f"Found columns: {', '.join(columns)}")
                
                if 'Company URL' not in columns:
                    logger.error("Required column 'Company URL' not found in CSV")
                    return None

                # Add file to database
                file_id = self.db.add_file(
                    filename=os.path.basename(file_path),
                    file_type='csv'
                )
                logger.info(f"Created file record with ID: {file_id}")

                # Process each row
                row_count = 0
                for row in csv_reader:
                    logger.debug(f"Processing row {row_count + 1}")
                    row_data = json.dumps(row)
                    self.db.add_file_data(
                        file_id=file_id,
                        row_data=row_data,
                        column_names=json.dumps(columns)
                    )
                    row_count += 1

                # Update row count
                self.db.update_row_count(file_id, row_count)
                logger.info(f"Successfully imported {row_count} rows from {file_path}")
                return file_id

        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            return None

    def crawl_company_websites(self, file_id: int) -> List[Dict]:
        """
        Crawl company websites and save data
        """
        try:
            logger.info(f"Starting website crawling for file_id: {file_id}")
            # Get company data from database
            file_data = self.db.get_file_data(file_id)
            if not file_data:
                logger.error(f"No data found for file_id: {file_id}")
                return []

            results = []
            total_companies = len(file_data)
            logger.info(f"Found {total_companies} companies to process")

            for index, (row_data, column_names) in enumerate(file_data, 1):
                try:
                    # Parse row data
                    row_dict = json.loads(row_data)
                    company_name = row_dict.get('Company Name', '')
                    website_url = row_dict.get('Company URL', '')

                    logger.info(f"Processing company {index}/{total_companies}: {company_name}")

                    if not website_url:
                        logger.warning(f"No company URL found for company: {company_name}")
                        continue

                    if not website_url.startswith(('http://', 'https://')):
                        website_url = f"https://{website_url}"
                        logger.info(f"Added https:// to URL: {website_url}")

                    # Crawl website
                    logger.info(f"Crawling website for {company_name}: {website_url}")
                    html_content = fetch_from_url(website_url)
                    
                    if not html_content:
                        logger.warning(f"No content retrieved from {website_url}")
                        continue

                    logger.info(f"Successfully crawled {website_url}")

                    # Save crawled data
                    crawl_id = self.db.save_crawled_data(
                        company_name=company_name,
                        url=website_url,
                        html_content=html_content,
                        source_file_id=file_id,
                        status='success',
                        error_message=None
                    )

                    if crawl_id:
                        logger.info(f"Saved crawled data with ID: {crawl_id}")
                        results.append({
                            'company_name': company_name,
                            'status': 'success',
                            'crawl_id': crawl_id
                        })
                    else:
                        logger.error(f"Failed to save crawled data for {company_name}")

                except Exception as e:
                    logger.error(f"Error processing company {company_name}: {str(e)}")
                    continue

            success_count = len([r for r in results if r['status'] == 'success'])
            logger.info(f"Completed crawling. Successfully processed {success_count} out of {total_companies} companies")
            return results

        except Exception as e:
            logger.error(f"Error crawling company websites: {str(e)}")
            return []

    def generate_cold_emails(self, file_id: int) -> None:
        """
        Generate cold emails for companies and save to database
        """
        try:
            logger.info(f"Starting cold email generation for file_id: {file_id}")
            
            # Get file data first
            file_data_rows = self.db.get_file_data(file_id)
            if not file_data_rows:
                logger.error("No file data found")
                return
                
            # Create a mapping of company names to their file data
            company_data_map = {}
            for row_data, column_names in file_data_rows:
                try:
                    row_dict = json.loads(row_data)
                    company_name = row_dict.get('Company Name', '')
                    if company_name:
                        company_data_map[company_name] = row_dict
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing row data: {str(e)}")
                    continue

            # Get crawled data
            crawled_data = self.db.get_crawled_data(source_file_id=file_id)
            if not crawled_data:
                logger.error("No crawled data found")
                return

            total_companies = len(crawled_data)
            logger.info(f"Found {total_companies} companies with crawled data")

            for index, data in enumerate(crawled_data, 1):
                try:
                    # Unpack data from crawled_data table
                    crawl_id, company_name, url, html_content, crawl_date, status, error = data
                    
                    logger.info(f"Processing company {index}/{total_companies}: {company_name}")

                    if status != 'success' or not html_content:
                        logger.warning(f"Skipping {company_name} due to missing or failed crawl")
                        continue
                    
                    logger.info(f"Generating cold email for: {company_name}")
                    
                    # Get the original file data for this company
                    company_data = company_data_map.get(company_name, {})
                    if not company_data:
                        logger.warning(f"No file data found for company: {company_name}")
                    
                    # Create complete company data dictionary
                    complete_company_data = {
                        'company_name': company_name,
                        'website': url,
                        'html_content': html_content,
                        'file_data': company_data,  # Include the original file data
                        'source_file_id': file_id
                    }
                    
                    logger.info(f"Complete company data: {json.dumps(complete_company_data, indent=2)}")
                    
                    # Use the complete data to generate the email
                    cold_email = get_cold_email_to_business(
                        company_profile=html_content,
                        business_name=company_name,
                        company_website=url,
                        company_data=complete_company_data  # Pass the complete data
                    )

                    if cold_email:
                        # Save to database
                        save_result = self.db.save_company_profile({
                            'company_name': company_name,
                            'profile_text': cold_email,
                            'source_file_id': file_id,
                            'status': 'success'
                        })
                        
                        if save_result:
                            logger.info(f"Successfully saved cold email for {company_name}")
                        else:
                            logger.error(f"Failed to save cold email for {company_name}")
                        
                        # Print the generated email
                        print("\n" + "="*50)
                        print(f"Cold Email for {company_name}")
                        print("="*50)
                        print(cold_email)
                        print("="*50 + "\n")

                except Exception as e:
                    logger.error(f"Error generating cold email for {company_name}: {str(e)}")
                    continue

            logger.info(f"Completed cold email generation for {total_companies} companies")

        except Exception as e:
            logger.error(f"Error in generate_cold_emails: {str(e)}")

    def send_cold_emails(self, file_id: int) -> None:
        """
        Send generated cold emails
        """
        try:
            logger.info("Starting to send cold emails...")
            
            # Get file details for metadata
            file_details = self.db.get_file_details(file_id)
            if not file_details:
                logger.error("Could not retrieve file details")
                return
                
            # Get all company profiles
            company_profiles = self.db.get_company_profiles(file_id)
            if not company_profiles:
                logger.warning(f"No company profiles found for file_id: {file_id}")
                return
            
            # Generate markdown document
            markdown_gen = MarkdownGenerator()
            markdown_path = markdown_gen.generate_markdown(
                company_profiles=company_profiles,
                file_metadata=file_details
            )
            
            if not markdown_path:
                logger.error("Failed to generate markdown document")
                return
                
            logger.info(f"Generated markdown document: {markdown_path}")
            
            # Prepare email batch
            email_batch = []
            for profile in company_profiles:
                company_name = profile.get('company_name', '')
                email_content = profile.get('profile_text', '')
                
                if not email_content:
                    logger.warning(f"No email content found for {company_name}")
                    continue
                
                # Get company email from file data
                company_data = self.db.get_company_details_by_file(file_id)
                if not company_data:
                    logger.warning(f"No company data found for {company_name}")
                    continue
                
                to_email = company_data.get('Company Email', '')
                if not to_email:
                    logger.warning(f"No email address found for {company_name}")
                    continue
                
                email_batch.append({
                    'to_email': to_email,
                    'subject': f"Partnership Opportunity with {MY_COMPANY_NAME}",
                    'content': email_content
                })
            
            if not email_batch:
                logger.warning("No valid emails to send")
                return
            
            # Process email batch with markdown attachment
            processor = BatchEmailProcessor()
            results = processor.process_batch(
                emails=email_batch,
                attachment_path=markdown_path,
                delay_seconds=5  # Add delay between emails
            )
            
            # Log results
            logger.info(f"Email sending complete:")
            logger.info(f"Total: {results['total']}")
            logger.info(f"Sent: {results['sent']}")
            logger.info(f"Failed: {results['failed']}")
            
            # Save results to database
            for detail in results['details']:
                self.db.update_email_status(
                    company_email=detail['email'],
                    status=detail['status'],
                    error_message=detail.get('reason', '')
                )
            
        except Exception as e:
            logger.error(f"Error sending cold emails: {str(e)}")

    def empty_all_tables(self):
        """Empty all tables in the database"""
        try:
            logger.info("Emptying all tables...")
            self.db.empty_tables()
            logger.info("Successfully emptied all tables")
        except Exception as e:
            logger.error(f"Error emptying tables: {str(e)}")

    def test_single_record(self, file_path: str):
        """Test the entire process with a single record"""
        try:
            logger.info("=== Starting Single Record Test ===")
            
            # Step 1: Process CSV
            logger.info("\n=== Step 1: Processing CSV ===")
            file_id = self.process_csv_file(file_path)
            if not file_id:
                logger.error("Failed to process CSV file")
                return
            
            # Get first record
            file_data = self.db.get_file_data(file_id)
            if not file_data:
                logger.error("No data found in CSV")
                return
                
            first_row = json.loads(file_data[0][0])
            logger.info("\nFirst Record Data:")
            for key, value in first_row.items():
                logger.info(f"{key}: {value}")
            
            # Step 2: Crawl Website
            logger.info("\n=== Step 2: Crawling Website ===")
            company_name = first_row.get('Company Name', '')
            website_url = first_row.get('Company URL', '')
            
            if not website_url:
                logger.error(f"No website URL found for company: {company_name}")
                return
                
            logger.info(f"Crawling website for {company_name}: {website_url}")
            html_content = fetch_from_url(website_url)
            
            if not html_content:
                logger.error("Failed to crawl website")
                return
                
            logger.info("Successfully crawled website")
            logger.info(f"HTML Content Length: {len(html_content)} characters")
            
            # Save crawled data
            crawl_id = self.db.save_crawled_data(
                company_name=company_name,
                url=website_url,
                html_content=html_content,
                source_file_id=file_id
            )
            logger.info(f"Saved crawled data with ID: {crawl_id}")
            
            # Step 3: Generate Cold Email
            logger.info("\n=== Step 3: Generating Cold Email ===")
            cold_email = get_cold_email_to_business(
                company_profile=html_content,
                business_name=company_name,
                company_website=website_url
            )
            
            if not cold_email:
                logger.error("Failed to generate cold email")
                return
                
            logger.info("\nGenerated Cold Email:")
            print("\n" + "="*50)
            print(cold_email)
            print("="*50 + "\n")
            
            # Save the email
            self.db.save_company_profile({
                'company_name': company_name,
                'profile_text': cold_email,
                'source_file_id': file_id,
                'status': 'success'
            })
            
            # Step 4: Test Email Sending (Optional)
            logger.info("\n=== Step 4: Email Sending Test ===")
            while True:
                send_test = input("\nWould you like to send a test email? (yes/no): ").strip().lower()
                if send_test in ['yes', 'no']:
                    break
                print("Please enter 'yes' or 'no'")
            
            if send_test == 'yes':
                self.send_cold_emails(file_id)
                logger.info("Test email sent")
            else:
                logger.info("Email sending test skipped")
            
            logger.info("\n=== Test Complete ===")
            
        except Exception as e:
            logger.error(f"Error in test process: {str(e)}")

    def generate_all_emails_doc(self):
        """Generate Markdown document with all emails from database"""
        try:
            # Get all profiles from database
            profiles = self.db.get_all_company_profiles()
            
            if not profiles:
                print("No emails found in the database.")
                return
            
            # Create metadata for the document
            metadata = {
                'filename': 'All Company Profiles',
                'row_count': len(profiles),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Generate Markdown
            md_gen = MarkdownGenerator()
            output_path = md_gen.generate_markdown(
                company_profiles=profiles,
                file_metadata=metadata
            )
            
            if output_path:
                print(f"\nSuccessfully generated Markdown document at: {output_path}")
                print(f"Total emails included: {len(profiles)}")
                print("\nYou can open this file in any Markdown viewer or editor to view the formatted emails.")
            else:
                print("Failed to generate Markdown document.")
                
        except Exception as e:
            logging.error(f"Error generating markdown document: {str(e)}")
            print("An error occurred while generating the document.")

def main():
    """
    Main function to run the EngageAI automation process
    """
    try:
        automation = MarketingAutomation()
        
        print("\n" + "="*50)
        print("Welcome to EngageAI - AI-Powered Cold Email Personalization")
        print("="*50)
        
        while True:
            print("\nWhat would you like to do?")
            print("1. Process new CSV file and generate cold emails")
            print("2. Send existing cold emails")
            print("3. Empty all tables")
            print("4. Test with single record")
            print("5. Generate Markdown document with all emails")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                # Get file path from user
                file_path = input("Enter the path to your CSV file: ").strip()
                logger.info(f"Starting process for file: {file_path}")
                
                # Process the CSV file
                logger.info("Step 1: Processing CSV file...")
                file_id = automation.process_csv_file(file_path)
                if not file_id:
                    logger.error("Failed to process CSV file")
                    continue

                # Crawl websites and save data
                logger.info("Step 2: Crawling websites...")
                results = automation.crawl_company_websites(file_id)
                logger.info(f"Successfully crawled {len(results)} companies")

                # Generate cold emails
                logger.info("Step 3: Generating cold emails...")
                automation.generate_cold_emails(file_id)
                
                # Ask user if they want to send emails
                while True:
                    send_emails = input("\nDo you want to send the generated emails? (yes/no): ").strip().lower()
                    if send_emails in ['yes', 'no']:
                        break
                    print("Please enter 'yes' or 'no'")
            
                if send_emails == 'yes':
                    logger.info("Step 4: Sending cold emails...")
                    automation.send_cold_emails(file_id)
                else:
                    logger.info("Email sending skipped as per user request")
                
            elif choice == "2":
                # List available file IDs with their details
                print("\nAvailable Cold Email Batches:")
                file_data = automation.db.get_all_files()
                
                if not file_data:
                    print("No existing cold email batches found.")
                    continue
                
                for file in file_data:
                    file_id, filename, file_type, row_count, created_at = file
                    print(f"Batch ID: {file_id}, File: {filename}, Created: {created_at}, Companies: {row_count or 0}")
                
                try:
                    file_id = int(input("\nEnter the Batch ID to send emails from: ").strip())
                    logger.info("Sending existing cold emails...")
                    automation.send_cold_emails(file_id)
                except ValueError:
                    logger.error("Invalid Batch ID. Please enter a number.")
                    continue
                
            elif choice == "3":
                while True:
                    confirm = input("\nAre you sure you want to empty all tables? This cannot be undone. (yes/no): ").strip().lower()
                    if confirm in ['yes', 'no']:
                        break
                    print("Please enter 'yes' or 'no'")
                
                if confirm == 'yes':
                    automation.empty_all_tables()
                    print("All tables have been emptied.")
                else:
                    print("Operation cancelled.")
                
            elif choice == "4":
                file_path = input("Enter the path to your CSV file: ").strip()
                automation.test_single_record(file_path)
                
            elif choice == "5":
                automation.generate_all_emails_doc()
                
            elif choice == "6":
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please enter 1-6.")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()
