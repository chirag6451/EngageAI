import os
from datetime import datetime
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    def __init__(self, output_dir="generated_docs"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_markdown(self, company_profiles: List[Dict], file_metadata: Dict = None) -> str:
        """
        Generate a markdown document from company profiles with enhanced formatting and metadata
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cold_emails_{timestamp}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            logger.info(f"Generating markdown document: {filepath}")
            
            with open(filepath, 'w') as f:
                # Write document header
                f.write("# Cold Email Campaign Report\n\n")
                
                # Add metadata section
                f.write("## Campaign Metadata\n\n")
                f.write(f"- **Generated Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if file_metadata:
                    f.write(f"- **Source**: {file_metadata.get('filename', 'N/A')}\n")
                    f.write(f"- **Total Companies**: {file_metadata.get('row_count', 0)}\n")
                    f.write(f"- **Creation Date**: {file_metadata.get('created_at', 'N/A')}\n")
                f.write("\n---\n\n")
                
                # Write table of contents
                f.write("## Table of Contents\n\n")
                for idx, profile in enumerate(company_profiles, 1):
                    company_name = profile.get('company_name', f'Company {idx}')
                    f.write(f"{idx}. [{company_name}](#{company_name.lower().replace(' ', '-')})\n")
                f.write("\n---\n\n")
                
                # Write each company profile
                f.write("## Generated Emails\n\n")
                for idx, profile in enumerate(company_profiles, 1):
                    # Handle both dictionary and tuple formats
                    if isinstance(profile, tuple):
                        # Convert tuple to dictionary if needed
                        profile = {
                            'company_name': profile[1] if len(profile) > 1 else f'Company {idx}',
                            'profile_text': profile[2] if len(profile) > 2 else '',
                            'status': profile[3] if len(profile) > 3 else 'N/A',
                            'created_at': profile[4] if len(profile) > 4 else 'N/A'
                        }
                    
                    company_name = profile.get('company_name', f'Company {idx}')
                    profile_text = profile.get('profile_text', '')
                    status = profile.get('status', 'N/A')
                    created_at = profile.get('created_at', 'N/A')
                    
                    f.write(f"### {company_name}\n\n")
                    f.write("#### Email Details\n\n")
                    f.write(f"- **Status**: {status}\n")
                    f.write(f"- **Created**: {created_at}\n\n")
                    f.write("#### Email Content\n\n")
                    f.write("```\n")
                    f.write(profile_text)
                    f.write("\n```\n\n")
                    f.write("---\n\n")
                
                # Add footer
                f.write("\n## Campaign Summary\n\n")
                f.write(f"- **Total Emails Generated**: {len(company_profiles)}\n")
                f.write(f"- **Generation Complete**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Successfully generated markdown document: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating markdown document: {str(e)}")
            return None

    def get_latest_document(self) -> str:
        """Get the path to the most recently generated document"""
        try:
            files = [f for f in os.listdir(self.output_dir) if f.endswith('.md')]
            if not files:
                return None
                
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(self.output_dir, x)))
            return os.path.join(self.output_dir, latest_file)
            
        except Exception as e:
            logger.error(f"Error getting latest document: {str(e)}")
            return None
