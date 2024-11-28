import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL

logger = logging.getLogger(__name__)

def format_email_content(content: str) -> str:
    """Format the email content with proper line breaks and spacing"""
    # Remove any existing excessive newlines
    content = '\n'.join(line for line in content.splitlines() if line.strip())
    return content

def send_email(
    to_email: str,
    subject: str,
    content: str,
    attachment_path: Optional[str] = None,
    cc_emails: List[str] = None,
    bcc_emails: List[str] = None
) -> bool:
    """
    Send an email with optional attachment and CC/BCC recipients
    """
    try:
        logger.info(f"Preparing to send email to: {to_email}")
        
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC recipients if provided
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
            
        # Format the email content
        formatted_content = format_email_content(content)
        msg.attach(MIMEText(formatted_content, 'plain'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            logger.info(f"Adding attachment: {attachment_path}")
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype="md")
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(attachment_path)
                )
                msg.attach(attachment)
        
        # Prepare recipient list
        recipients = [to_email]
        if cc_emails:
            recipients.extend(cc_emails)
        if bcc_emails:
            recipients.extend(bcc_emails)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, recipients, msg.as_string())
            
        logger.info(f"Successfully sent email to {to_email}")
        if attachment_path:
            logger.info(f"Attachment {os.path.basename(attachment_path)} was included")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def send_email_with_attachment(
    to_email: str,
    subject: str,
    content: str,
    attachment_path: str,
    cc_emails: List[str] = None,
    bcc_emails: List[str] = None
) -> bool:
    """
    Send an email with an attachment
    """
    try:
        logger.info(f"Preparing to send email with attachment to: {to_email}")
        
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC recipients if provided
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
            
        # Format and add the email content
        formatted_content = format_email_content(content)
        msg.attach(MIMEText(formatted_content, 'plain'))
        
        # Add attachment
        if os.path.exists(attachment_path):
            logger.info(f"Adding attachment: {attachment_path}")
            with open(attachment_path, 'rb') as f:
                part = MIMEApplication(f.read(), _subtype="docx")
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(attachment_path)
                )
                msg.attach(part)
        else:
            logger.error(f"Attachment not found: {attachment_path}")
            return False
        
        # Prepare list of all recipients
        recipients = [to_email]
        if cc_emails:
            recipients.extend(cc_emails)
        if bcc_emails:
            recipients.extend(bcc_emails)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, recipients, msg.as_string())
            
        logger.info(f"Successfully sent email with attachment to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email with attachment: {str(e)}")
        return False

class BatchEmailProcessor:
    def __init__(self):
        self.sent_count = 0
        self.failed_count = 0
        
    def process_batch(
        self,
        emails: List[dict],
        attachment_path: Optional[str] = None,
        delay_seconds: int = 5
    ) -> dict:
        """
        Process a batch of emails with optional attachment
        """
        import time
        
        results = {
            'total': len(emails),
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        for email_data in emails:
            try:
                to_email = email_data.get('to_email')
                subject = email_data.get('subject')
                content = email_data.get('content')
                cc_list = email_data.get('cc', [])
                bcc_list = email_data.get('bcc', [])
                
                if not all([to_email, subject, content]):
                    logger.error(f"Missing required email fields for {to_email}")
                    results['failed'] += 1
                    results['details'].append({
                        'email': to_email,
                        'status': 'failed',
                        'reason': 'Missing required fields'
                    })
                    continue
                
                success = send_email(
                    to_email=to_email,
                    subject=subject,
                    content=content,
                    attachment_path=attachment_path,
                    cc_emails=cc_list,
                    bcc_emails=bcc_list
                )
                
                if success:
                    results['sent'] += 1
                    results['details'].append({
                        'email': to_email,
                        'status': 'sent',
                        'attachment': bool(attachment_path)
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'email': to_email,
                        'status': 'failed',
                        'reason': 'Send failed'
                    })
                
                # Add delay between emails
                if delay_seconds > 0 and email_data != emails[-1]:
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                logger.error(f"Error processing email to {to_email}: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'email': to_email,
                    'status': 'failed',
                    'reason': str(e)
                })
        
        return results
