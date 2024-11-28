import os
import logging
import mimetypes
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List
import markdown

def format_email_content(cold_email: str) -> str:
    """Convert the cold email text to HTML format using markdown"""
    return markdown.markdown(cold_email)

def send_email(subject: str, body: str, to_email: List[str], attachments: List[str] = [], is_html: bool = False):
    from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL
    
    MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
    allowed_extensions = ['.pdf', '.txt', '.docx', '.jpg', '.png', '.zip']
    
    print("Sending email...")
    msg = EmailMessage()
    
    # Set content based on whether it's HTML or plain text
    if is_html:
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)
    
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    
    # Ensure the email addresses are stripped of leading/trailing whitespace
    to_email_list = [email.strip() for email in to_email]
    msg['To'] = ", ".join(to_email_list)

    total_attachment_size = 0
    for attachment in attachments:
        if not os.path.isfile(attachment):
            logging.warning(f"Attachment {attachment} not found. Skipping.")
            continue
        
        file_size = os.path.getsize(attachment)
        if total_attachment_size + file_size > MAX_ATTACHMENT_SIZE:
            logging.warning(f"The size of attachment is {file_size}")
            logging.warning("Total attachment size exceeds the limit. Skipping additional attachments.")
            msg.set_content(f"{body}\n\nAttachments size exceeds the limit. Please download the files from the link provided.")
            break
        
        extension = os.path.splitext(attachment)[1]
        if extension not in allowed_extensions:
            logging.warning(f"File type {extension} not allowed. Skipping attachment: {attachment}")
            continue
        
        total_attachment_size += file_size
        ctype, encoding = mimetypes.guess_type(attachment)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        
        with open(attachment, 'rb') as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(attachment))
            logging.info(f"Added '{attachment}' to email.")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email_list, msg.as_string())
            print("Email sent successfully!")
            logging.info("Email sent successfully!")
            return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_email_with_attachment(recipient_email: str, subject: str, body: str, attachment_path: str) -> bool:
    """
    Send an email with an attachment using SMTP
    """
    from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
    logger = logging.getLogger()
    
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            
        # Encode the attachment
        encoders.encode_base64(part)
        
        # Add header for attachment
        filename = os.path.basename(attachment_path)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )

        # Add attachment to message
        msg.attach(part)

        # Create SMTP session
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email with attachment sent successfully to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Error sending email with attachment: {str(e)}")
        return False
