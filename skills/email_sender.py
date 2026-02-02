import smtplib
import re
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_email(to: str, subject: str, body: str) -> str:
    """Send email using Gmail SMTP."""
    try:
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, to):
            return "Invalid email address format."

        # Get credentials from environment
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')

        if not email_address or not email_password:
            return "Email credentials not configured in .env file."

        # Create message
        msg = EmailMessage()
        msg['From'] = email_address
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(body)

        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)

        return f"Email sent successfully to {to}."

    except smtplib.SMTPAuthenticationError:
        return "Email authentication failed. Check your credentials."
    except smtplib.SMTPException:
        return "Failed to send email. SMTP error occurred."
    except Exception:
        return "Failed to send email due to an unexpected error."
