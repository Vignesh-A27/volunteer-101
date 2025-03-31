import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sender_email = st.secrets['VOL_LINK_EMAIL']
        self.app_password = st.secrets['VOL_LINK_PASSWORD']
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 465

    def _create_message(self, to_email, subject, body):
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        return message

    def _send_email(self, to_email, subject, body):
        try:
            if not self.sender_email or not self.app_password:
                logger.error(f'Email credentials not properly configured. Sender: {self.sender_email is not None}, Password: {self.app_password is not None}')
                return False

            message = self._create_message(to_email, subject, body)
            
            logger.info(f'Attempting to connect to SMTP server: {self.smtp_server}:{self.smtp_port}')
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10) as server:
                try:
                    server.login(self.sender_email, self.app_password)
                    logger.info('SMTP authentication successful')
                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f'SMTP Authentication failed. Please check your email and app password. Error: {str(e)}')
                    return False
                
                try:
                    server.send_message(message)
                    logger.info(f'Email sent successfully to {to_email}')
                    return True
                except smtplib.SMTPRecipientsRefused as e:
                    logger.error(f'Invalid recipient email address {to_email}: {str(e)}')
                    return False
                except smtplib.SMTPException as e:
                    logger.error(f'Error sending email: {str(e)}')
                    return False
                
        except smtplib.SMTPConnectError as e:
            logger.error(f'Failed to connect to SMTP server: {str(e)}')
            return False
        except Exception as e:
            logger.error(f'Unexpected error while sending email to {to_email}: {str(e)}')
            return False

    def send_event_registration_confirmation(self, volunteer_email, volunteer_name, event_data, org_name):
        subject = f'Event Registration Confirmation - {event_data.get("title", "Untitled Event")}'
        body = f"""Dear {volunteer_name},

Thank you for registering for {event_data.get("title", "Untitled Event")}!

Event Details:
Date: {event_data.get("date", "TBD")}
Location: {event_data.get("location", "TBD")}
Organization: {org_name}

Your application is currently under review. You will receive another email once the organization has made a decision.

We appreciate your commitment to making a difference in our community.

Best regards,
Volunteer Management Team"""

        return self._send_email(volunteer_email, subject, body)

    def send_organization_event_notification(self, org_email, volunteer_name, event_name, action):
        subject = f'Volunteer {action.capitalize()} Notification - {event_name}'
        body = f"""Dear Organization,

This is to inform you that {volunteer_name} has {action} to participate in {event_name}.

Volunteer Details:
Name: {volunteer_name}
Action: {action.capitalize()}
Event: {event_name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Volunteer Management System"""

        return self._send_email(org_email, subject, body)

    def send_volunteer_acceptance_notification(self, volunteer_email, volunteer_name, event_name, org_name):
        subject = f'Application Accepted - {event_name}'
        body = f"""Dear {volunteer_name},

Congratulations! Your application to participate in {event_name} has been accepted by {org_name}.

Thank you for your commitment to volunteering. The organization will contact you with further details about the event.

Please make sure to:
1. Mark this date in your calendar
2. Arrive on time
3. Contact the organization if you need to cancel

Best regards,
Volunteer Management Team"""

        return self._send_email(volunteer_email, subject, body)

    def send_volunteer_rejection_notification(self, volunteer_email, volunteer_name, event_name, org_name):
        subject = f'Application Status Update - {event_name}'
        body = f"""Dear {volunteer_name},

Thank you for your interest in {event_name}. Unfortunately, {org_name} is unable to accept your application at this time.

This could be due to various reasons such as:
- Limited volunteer positions
- Specific skill requirements
- Schedule constraints

We encourage you to:
1. Explore other volunteering opportunities on our platform
2. Update your profile with additional skills
3. Apply for future events that match your interests

Best regards,
Volunteer Management Team"""

        return self._send_email(volunteer_email, subject, body)
