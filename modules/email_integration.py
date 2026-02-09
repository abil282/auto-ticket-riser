"""
Email Integration Module
Handles Office 365 email integration and email-based ticket creation
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
from datetime import datetime


class Office365Integration:
    """Handle Office 365 email integration"""
    
    def __init__(self, smtp_server='smtp.office365.com', smtp_port=587):
        """
        Initialize Office 365 email integration
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP port
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.sender_password = None
        self.authenticated = False
    
    def authenticate(self, email, password):
        """
        Authenticate with Office 365
        
        Args:
            email (str): Office 365 email address
            password (str): Office 365 password or app password
            
        Returns:
            bool: True if authenticated successfully
        """
        try:
            self.sender_email = email
            self.sender_password = password
            
            # Test connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(email, password)
            server.quit()
            
            self.authenticated = True
            return True
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            self.authenticated = False
            return False
    
    def send_email(self, recipient, subject, body, html_body=None, attachments=None):
        """
        Send email via Office 365
        
        Args:
            recipient (str or list): Email recipient(s)
            subject (str): Email subject
            body (str): Plain text body
            html_body (str, optional): HTML formatted body
            attachments (list, optional): List of file paths to attach
            
        Returns:
            bool: True if sent successfully
        """
        if not self.authenticated:
            print("Not authenticated. Please authenticate first.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            
            if isinstance(recipient, list):
                message['To'] = ', '.join(recipient)
            else:
                message['To'] = recipient
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                message.attach(MIMEText(html_body, 'html'))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename= {filepath.split("/")[-1]}')
                        message.attach(part)
                    except Exception as e:
                        print(f"Failed to attach {filepath}: {str(e)}")
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(message)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def send_ticket_confirmation(self, recipient_email, ticket_id, ticket_subject, team_email):
        """
        Send ticket creation confirmation email
        
        Args:
            recipient_email (str): Recipient email address
            ticket_id (str): Created ticket ID
            ticket_subject (str): Ticket subject/issue
            team_email (str): Assigned team email
            
        Returns:
            bool: True if sent successfully
        """
        subject = f"Ticket Confirmation - {ticket_id}"
        
        body = f"""
Dear User,

Your support ticket has been successfully created. Here are the details:

Ticket ID: {ticket_id}
Subject: {ticket_subject}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Assigned Team: {team_email}
Status: Open

Your ticket has been assigned to the appropriate support team. 
You will receive updates as your ticket is being worked on.

Please keep your ticket ID ({ticket_id}) for future reference.

Best regards,
IT Support System
        """
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4472C4;">Ticket Confirmation</h2>
        <p>Dear User,</p>
        <p>Your support ticket has been successfully created. Here are the details:</p>
        
        <div style="background-color: #f5f5f5; padding: 20px; border-left: 4px solid #4472C4; margin: 20px 0;">
            <p><strong>Ticket ID:</strong> {ticket_id}</p>
            <p><strong>Subject:</strong> {ticket_subject}</p>
            <p><strong>Created:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Assigned Team:</strong> {team_email}</p>
            <p><strong>Status:</strong> Open</p>
        </div>
        
        <p>Your ticket has been assigned to the appropriate support team. 
        You will receive updates as your ticket is being worked on.</p>
        
        <p><strong>Please keep your ticket ID ({ticket_id}) for future reference.</strong></p>
        
        <p>Best regards,<br>IT Support System</p>
    </div>
</body>
</html>
        """
        
        return self.send_email(recipient_email, subject, body, html_body)
    
    def send_ticket_update(self, recipient_email, ticket_id, update_message, assigned_to=None):
        """Send ticket update notification"""
        subject = f"Ticket Update - {ticket_id}"
        
        body = f"""
Dear User,

Your ticket {ticket_id} has been updated.

Update: {update_message}
{"Assigned to: " + assigned_to if assigned_to else ""}
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please reply to this email or log into the support portal for more details.

Best regards,
IT Support System
        """
        
        return self.send_email(recipient_email, subject, body)
    
    def send_team_notification(self, team_email, ticket_id, ticket_data):
        """Send notification to support team about new ticket"""
        subject = f"New Ticket Assigned - {ticket_id}"
        
        body = f"""
New ticket has been assigned to your team.

Ticket ID: {ticket_id}
User: {ticket_data.get('user_name', 'Unknown')}
Email: {ticket_data.get('user_email', 'Unknown')}
Department: {ticket_data.get('department', 'Unknown')}
Category: {ticket_data.get('category', 'General')}
Priority: {ticket_data.get('priority', 'P3 - Medium')}
Issue: {ticket_data.get('corrected_description', 'N/A')[:200]}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please log into the support portal to view and respond to this ticket.

Best regards,
Ticket Management System
        """
        
        return self.send_email(team_email, subject, body)


class EmailTicketParser:
    """Parse incoming emails for ticket creation"""
    
    @staticmethod
    def extract_ticket_info(email_body, sender_email=None):
        """
        Extract ticket information from email body
        
        Args:
            email_body (str): Email body text
            sender_email (str, optional): Sender email address
            
        Returns:
            dict: Extracted ticket information
        """
        # Extract common patterns
        priority = 'P3 - Medium'  # Default
        category = 'General'
        
        # Check for priority indicators
        if any(word in email_body.lower() for word in ['urgent', 'critical', 'asap', 'emergency']):
            priority = 'P1 - Critical'
        elif any(word in email_body.lower() for word in ['high', 'important']):
            priority = 'P2 - High'
        
        # First paragraph or subject is usually the issue description
        lines = email_body.split('\n')
        issue_description = lines[0] if lines else email_body[:200]
        
        return {
            'user_email': sender_email,
            'original_description': issue_description,
            'priority': priority,
            'category': category,
            'source': 'email'
        }
    
    @staticmethod
    def extract_email_patterns(email_body):
        """Extract additional info patterns from email"""
        info = {}
        
        # Extract phone numbers
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, email_body)
        if phones:
            info['phone'] = phones[0]
        
        # Extract mentions of system/software
        systems = ['windows', 'mac', 'linux', 'outlook', 'teams', 'excel', 'word']
        for system in systems:
            if system in email_body.lower():
                info['system'] = system
                break
        
        return info
