import streamlit as st
import pandas as pd
import json
import os
import logging
from datetime import datetime
from crawl_with_ai import fetch_from_url
from cold_email_generator import get_cold_email_to_business, extract_company_info
from ai_profile_generator import AIProfileGenerator
from temp_config import (
    MY_NAME, MY_DESIGNATION, MY_COMPANY_NAME, MY_LINKEDIN, 
    MY_PHONE, MY_EMAIL, MY_COMPANY_PROFILE, OPENAI_API_KEY
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize AI Profile Generator
profile_generator = AIProfileGenerator()

def process_company(company_name: str, website_url: str, location: str = None, config: dict = None) -> dict:
    """Process a single company and generate email content"""
    try:
        if not config:
            raise ValueError("Configuration is required for email generation")
            
        if not website_url:
            return {
                "status": "error",
                "company_name": company_name,
                "message": f"No URL provided for {company_name}"
            }

        if not website_url.startswith(('http://', 'https://')):
            website_url = f"https://{website_url}"

        # Crawl website
        html_content = fetch_from_url(website_url)
        if not html_content:
            return {
                "status": "error",
                "company_name": company_name,
                "message": f"Could not fetch content from {website_url}"
            }

        # Extract company info
        company_info = extract_company_info(html_content)
        
        # Generate company profile using AI
        company_data = {
            'company_name': company_name,
            'html_content': html_content
        }
        profile_result = profile_generator.generate_company_profile(company_data)
        
        if profile_result['status'] == 'success':
            company_profile = profile_result['profile']
            
            # Add location to company data if available
            if location:
                company_data['file_data'] = {'Location': location}
            
            # Generate email with custom config
            email_content = get_cold_email_to_business(
                company_profile=company_profile,
                business_name=company_name,
                company_website=website_url,
                company_data=company_data if location else None,
                config=config
            )
            
            return {
                "status": "success",
                "company_name": company_name,
                "email_content": email_content,
                "company_profile": company_profile
            }
        else:
            return {
                "status": "error",
                "company_name": company_name,
                "message": profile_result.get('error', 'Failed to generate profile')
            }
            
    except Exception as e:
        logger.error(f"Error processing company {company_name}: {str(e)}")
        return {
            "status": "error",
            "company_name": company_name,
            "message": str(e)
        }

def save_emails_to_file(emails: list) -> str:
    """Save generated emails to a text file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_emails_{timestamp}.txt"
    
    with open(filename, "w") as f:
        for email in emails:
            if email["status"] == "success":
                f.write(f"\n{'='*50}\n")
                f.write(f"Email for: {email['company_name']}\n")
                f.write(f"{'='*50}\n\n")
                f.write(email["email_content"])
                f.write("\n\n")
    
    return filename

def main():
    st.title("EngageAI - AI-Powered Cold Email Personalization")
    st.write("Upload a CSV file with company information to generate personalized cold emails.")

    # Configuration Section
    with st.expander("⚙️ Configuration", expanded=False):
        st.subheader("Personal and Company Information")
        config = {
            'MY_NAME': st.text_input("Your Name", value=MY_NAME, key="name_input"),
            'MY_DESIGNATION': st.text_input("Your Designation", value=MY_DESIGNATION, key="designation_input"),
            'MY_COMPANY_NAME': st.text_input("Company Name", value=MY_COMPANY_NAME, key="company_input"),
            'MY_LINKEDIN': st.text_input("LinkedIn Profile", value=MY_LINKEDIN, key="linkedin_input"),
            'MY_PHONE': st.text_input("Phone Number", value=MY_PHONE, key="phone_input"),
            'MY_EMAIL': st.text_input("Email", value=MY_EMAIL, key="email_input"),
            'MY_COMPANY_PROFILE': st.text_area("Company Profile", value=MY_COMPANY_PROFILE, height=200, key="profile_input")
        }

    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        
        # Check required columns
        required_columns = ['Company Name', 'Company URL']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return
        
        # Check for Location column
        has_location = 'Location' in df.columns
        if has_location:
            st.info("Found 'Location' column - will use it for weather-based personalization!")
        
        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(df)
        
        # Allow user to select companies to process
        st.subheader("Select Companies to Process")
        all_companies = st.checkbox("Select All", value=False)
        
        if all_companies:
            selected_indices = list(range(len(df)))
        else:
            options = [f"{row['Company Name']} ({row['Company URL']})" for _, row in df.iterrows()]
            selected_options = st.multiselect(
                "Choose companies to process:",
                options=options,
                format_func=lambda x: x.split(" (")[0]
            )
            selected_indices = [options.index(opt) for opt in selected_options]
        
        # Process button
        if len(selected_indices) > 0 and st.button("Generate Emails"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Container for results
            results = []
            total_companies = len(selected_indices)
            
            # Process selected companies
            for idx, index in enumerate(selected_indices):
                row = df.iloc[index]
                company_name = row['Company Name']
                website_url = row['Company URL']
                location = row['Location'] if has_location else None
                
                # Update status
                status_text.text(f"Processing {company_name}...")
                progress = (idx + 1) / total_companies
                progress_bar.progress(progress)
                
                # Process company with config
                result = process_company(company_name, website_url, location, config)
                results.append(result)
            
            # Show completion
            progress_bar.progress(100)
            status_text.text("Processing complete!")
            
            # Display results summary
            successful = len([r for r in results if r["status"] == "success"])
            failed = len([r for r in results if r["status"] == "error"])
            
            st.subheader("Processing Results")
            st.write(f"Successfully processed: {successful}")
            st.write(f"Failed: {failed}")
            
            # Show errors if any
            if failed > 0:
                st.subheader("Errors")
                for result in results:
                    if result["status"] == "error":
                        company_name = result.get('company_name', 'Unknown Company')
                        error_msg = result.get('message', 'Unknown error')
                        st.error(f"{company_name}: {error_msg}")
            
            # Preview section
            st.subheader("Email Previews")
            for result in results:
                if result["status"] == "success":
                    with st.expander(f"Preview email for {result['company_name']}"):
                        st.markdown("### Email Content")
                        st.text_area("", result["email_content"], height=200, key=f"email_{result['company_name']}")
                        st.markdown("### Company Profile")
                        st.text_area("", result["company_profile"], height=200, key=f"profile_{result['company_name']}")
            
            # Download button
            if successful > 0:
                filename = save_emails_to_file(results)
                with open(filename, "rb") as f:
                    st.download_button(
                        label="Download Email Bodies",
                        data=f,
                        file_name=filename,
                        mime="text/plain"
                    )
                # Clean up the file after offering download
                os.remove(filename)

if __name__ == "__main__":
    main()
