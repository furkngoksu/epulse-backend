import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    
    def __init__(self):
        self.enabled = bool(settings.MAILEROO_API_KEY)
        if not self.enabled:
            logger.warning("Email service disabled: MAILEROO_API_KEY not set")
            return
        
        self.api_url = "https://smtp.maileroo.com/send"
        self.api_key = settings.MAILEROO_API_KEY
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
    
    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        if not self.enabled:
            logger.warning(f"Email disabled: OTP to {to_email}")
            return False
        
        try:
            payload = {
                'from': f'{self.from_name} <{self.from_email}>',
                'to': to_email,
                'subject': 'E-Pulse - Password Reset Code',
                'html': f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Password Reset Request</h2>
                    <p>Your verification code:</p>
                    <div style="background: #f5f5f5; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                        {otp_code}
                    </div>
                    <p style="color: #666;">This code expires in 10 minutes.</p>
                    <p style="color: #666;">If you didn't request this, ignore this email.</p>
                </div>
                """
            }
            
            response = requests.post(
                self.api_url,
                headers={'X-API-Key': self.api_key},
                data=payload
            )
            
            if response.status_code == 200 and response.json().get('success'):
                logger.info("OTP email sent successfully", extra={"to": to_email})
                return True
            else:
                error_message = response.json().get('message', 'Unknown error')
                logger.error(f"Failed to send OTP: {error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send OTP: {str(e)}")
            return False
    
    def send_password_changed_notification(self, to_email: str) -> bool:
        if not self.enabled:
            logger.warning(f"Email disabled: Password changed to {to_email}")
            return False
        
        try:
            payload = {
                'from': f'{self.from_name} <{self.from_email}>',
                'to': to_email,
                'subject': 'E-Pulse - Password Changed',
                'html': """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Password Changed Successfully</h2>
                    <p>Your password has been changed.</p>
                    <p style="color: #666;">If you didn't make this change, contact support immediately.</p>
                </div>
                """
            }
            
            response = requests.post(
                self.api_url,
                headers={'X-API-Key': self.api_key},
                data=payload
            )
            
            if response.status_code == 200 and response.json().get('success'):
                logger.info("Password changed notification sent successfully", extra={"to": to_email})
                return True
            else:
                error_message = response.json().get('message', 'Unknown error')
                logger.error(f"Failed to send notification: {error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False


email_service = EmailService()
