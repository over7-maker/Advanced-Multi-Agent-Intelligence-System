"""
Email Service for AMAS
Handles email sending for feedback confirmations and notifications
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails via SMTP"""
    
    def __init__(self):
        """Initialize email service with configuration from environment"""
        self.smtp_server = os.getenv("SMTP_SERVER", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@amas.ai")
        self.from_name = os.getenv("SMTP_FROM_NAME", "AMAS Intelligence System")
        self.enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        
        if not self.enabled:
            logger.info("Email service is disabled (EMAIL_ENABLED=false)")
    
    async def send_feedback_confirmation(
        self,
        to_email: str,
        to_name: str,
        feedback_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send feedback confirmation email
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            feedback_id: Optional feedback ID for reference
            
        Returns:
            Dict with status and error message if any
        """
        if not self.enabled:
            logger.debug(f"Email service disabled, skipping confirmation to {to_email}")
            return {"status": "skipped", "reason": "email_disabled"}
        
        try:
            subject = "Thank you for your feedback - AMAS"
            
            # Create HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2180a5 0%, #5e5240 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #2180a5; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Thank You for Your Feedback!</h1>
                    </div>
                    <div class="content">
                        <p>Dear {to_name},</p>
                        <p>We have received your feedback and truly appreciate you taking the time to share your thoughts with us.</p>
                        <p>Your input helps us improve AMAS and provide better service to all our users.</p>
                        {f'<p><strong>Feedback ID:</strong> {feedback_id}</p>' if feedback_id else ''}
                        <p>If you have any additional questions or concerns, please don't hesitate to reach out to us.</p>
                        <p>Best regards,<br><strong>The AMAS Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                        <p>&copy; 2025 AMAS Intelligence System. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_body = f"""
            Thank You for Your Feedback!
            
            Dear {to_name},
            
            We have received your feedback and truly appreciate you taking the time to share your thoughts with us.
            
            Your input helps us improve AMAS and provide better service to all our users.
            {f'Feedback ID: {feedback_id}' if feedback_id else ''}
            
            If you have any additional questions or concerns, please don't hesitate to reach out to us.
            
            Best regards,
            The AMAS Team
            
            ---
            This is an automated message. Please do not reply to this email.
            © 2025 AMAS Intelligence System. All rights reserved.
            """
            
            return await self._send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
        except Exception as e:
            logger.error(f"Failed to send feedback confirmation email: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> Dict[str, any]:
        """
        Send email via SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body
            
        Returns:
            Dict with status and error message if any
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_username and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return {"status": "success", "recipient": to_email}
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            return {"status": "error", "error": f"SMTP error: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

