import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def send_contact_form_notification(name: str, email: str, message: str) -> bool:
    """
    Send email notification when someone submits the contact form.

    Args:
        name: Name of the person who submitted the form
        email: Email of the person who submitted the form
        message: Message content from the form

    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'New Contact Form Submission from {name}'
        msg['From'] = f'{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>'
        msg['To'] = settings.NOTIFICATION_EMAIL
        msg['Reply-To'] = email

        # Create plain text version
        text_content = f"""
New Contact Form Submission

From: {name}
Email: {email}

Message:
{message}

---
This notification was sent from your portfolio website at cmack.dev
"""

        # Create HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'DM Sans', Arial, sans-serif; line-height: 1.6; color: #1a202c; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #5b8eb3 0%, #2c5282 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px; }}
        .field {{ margin-bottom: 20px; }}
        .field-label {{ font-weight: 600; color: #5b8eb3; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }}
        .field-value {{ color: #1a202c; font-size: 16px; }}
        .message-box {{ background: #f7fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #5b8eb3; margin-top: 10px; }}
        .footer {{ text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 New Contact Form Submission</h1>
        </div>
        <div class="content">
            <div class="field">
                <div class="field-label">From</div>
                <div class="field-value">{name}</div>
            </div>
            <div class="field">
                <div class="field-label">Email</div>
                <div class="field-value"><a href="mailto:{email}" style="color: #5b8eb3; text-decoration: none;">{email}</a></div>
            </div>
            <div class="field">
                <div class="field-label">Message</div>
                <div class="message-box">{message.replace(chr(10), '<br>')}</div>
            </div>
            <div class="footer">
                This notification was sent from your portfolio website at <strong>cmack.dev</strong>
            </div>
        </div>
    </div>
</body>
</html>
"""

        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Email not sent.")
            return False

        # Use SMTP with STARTTLS for better compatibility (especially on PythonAnywhere)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Contact form notification sent successfully for submission from {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send contact form notification: {str(e)}")
        return False
