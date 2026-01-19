"""
Email service for sending notifications via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

def send_email_notification(
    admin_emails: str,
    sender_name: str,
    sender_email: str,
    subject: Optional[str],
    message: str
) -> bool:
    """
    Send email notification to admin emails when a new contact message is received
    
    Args:
        admin_emails: Comma-separated list of admin email addresses
        sender_name: Name of the person who sent the contact message
        sender_email: Email of the person who sent the contact message
        subject: Subject of the contact message
        message: Message content
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get SMTP settings from environment variables
        smtp_enabled = os.getenv("SMTP_ENABLED", "false").lower() == "true"
        if not smtp_enabled:
            logger.info("SMTP is disabled in environment variables. Skipping email notification.")
            return False
        
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not admin_emails or not smtp_username or not smtp_password:
            logger.warning("Email configuration incomplete. Skipping email notification.")
            return False
        
        # Parse admin emails
        recipient_list = [email.strip() for email in admin_emails.split(',') if email.strip()]
        if not recipient_list:
            logger.warning("No admin emails configured. Skipping email notification.")
            return False
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = f"New Contact Message: {subject or 'No Subject'}"
        
        # Create email body
        body = f"""
A new message has been received on your website.

From: {sender_name} ({sender_email})
Subject: {subject or 'No Subject'}

Message:
{message}

---
This is an automated notification from your website contact form.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email using SMTP
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent successfully to {len(recipient_list)} admin(s)")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in send_email_notification: {e}")
        return False
