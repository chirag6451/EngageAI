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

            for index, row in enumerate(file_data, 1):
                try:
                    # Parse row data
                    row_dict = json.loads(row[0])
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
                        source_file_id=file_id
                    )
                    logger.info(f"Saved crawled data with ID: {crawl_id}")
                    results.append({'company_name': company_name, 'status': 'success'})

                except Exception as e:
                    logger.error(f"Error processing company {company_name}: {str(e)}")
                    continue

            logger.info(f"Completed crawling. Successfully processed {len(results)} out of {total_companies} companies")
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
            # Get crawled data directly from crawled_data table
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
                    
                    # Use the crawled HTML content to generate the email
                    cold_email = get_cold_email_to_business(
                        company_profile=html_content,
                        founder_name="",  # You might want to extract this from HTML if possible
                        business_name=company_name,
                        company_website=url
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
            # Get all generated cold emails
            cold_emails = self.db.get_company_profiles(file_id)
            
            if not cold_emails:
                logger.warning("No cold emails found to send")
                return

            total_emails = len(cold_emails)
            logger.info(f"Found {total_emails} cold emails to send")

            for index, email_data in enumerate(cold_emails, 1):
                try:
                    company_name = email_data.get('company_name', 'Unknown Company')
                    email_content = email_data.get('profile_text', '')
                    
                    if not email_content:
                        logger.warning(f"No email content found for {company_name}")
                        continue

                    # Format the email content as HTML
                    html_content = format_email_content(email_content)
                    
                    # Send the email
                    subject = f"Business Proposal for {company_name}"
                    success = send_email(
                        subject=subject,
                        body=html_content,
                        to_email=TO_EMAILS,
                        is_html=True
                    )
                    
                    if success:
                        logger.info(f"Successfully sent email {index}/{total_emails} to {company_name}")
                    else:
                        logger.error(f"Failed to send email to {company_name}")

                except Exception as e:
                    logger.error(f"Error sending email for {company_name}: {str(e)}")
                    continue

            logger.info("Completed sending all cold emails")

        except Exception as e:
            logger.error(f"Error in send_cold_emails: {str(e)}")

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

def main():
    """
    Main function to run the marketing automation process
    """
    try:
        # Initialize the automation class
        automation = MarketingAutomation()
        
        while True:
            print("\nCold Email Marketing Automation")
            print("1. Process new CSV file and generate emails")
            print("2. Send existing cold emails")
            print("3. Empty all tables")
            print("4. Test with single record")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
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
                print("Exiting program...")
                break
            
            else:
                print("Invalid choice. Please enter 1-5.")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()
