import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    
    def __init__(self):
        self.enabled = bool(settings.BREVO_API_KEY)
        if not self.enabled:
            return
        
        # Configure Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        if not self.enabled:
            logger.warning(f"Email disabled: OTP to {to_email}")
            return False
        
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"email": settings.FROM_EMAIL, "name": settings.FROM_NAME},
                subject="E-Pulse - Password Reset Code",
                html_content=f"""
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
            )
            
            self.api_instance.send_transac_email(send_smtp_email)
            logger.info("OTP email sent successfully", extra={"to": to_email})
            return True
        except ApiException as e:
            logger.error(f"Failed to send OTP: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send OTP: {str(e)}")
            return False
    
    def send_password_changed_notification(self, to_email: str) -> bool:
        if not self.enabled:
            logger.warning(f"Email disabled: Password changed to {to_email}")
            return False
        
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"email": settings.FROM_EMAIL, "name": settings.FROM_NAME},
                subject="E-Pulse - Password Changed",
                html_content="""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Password Changed Successfully</h2>
                    <p>Your password has been changed.</p>
                    <p style="color: #666;">If you didn't make this change, contact support immediately.</p>
                </div>
                """
            )
            
            self.api_instance.send_transac_email(send_smtp_email)
            logger.info("Password changed notification sent successfully", extra={"to": to_email})
            return True
        except ApiException as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False


email_service = EmailService()
