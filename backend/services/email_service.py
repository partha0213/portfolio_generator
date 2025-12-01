import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SMTP_USER")
        self.sender_password = os.getenv("SMTP_PASSWORD")
    
    def generate_verification_code(self, length=6):
        """Generate a random 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_email(self, recipient_email: str, verification_code: str, full_name: str = None):
        """Send verification email with 6-digit code"""
        try:
            if not self.sender_email or not self.sender_password:
                print("⚠️ Email credentials not configured. Verification code:", verification_code)
                return True
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Portfolio Generator - Email Verification"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Plain text version
            text = f"""\
Hi {full_name or 'User'},

Your email verification code is: {verification_code}

Please enter this code to complete your account registration.
This code will expire in 10 minutes.

Best regards,
Portfolio Generator Team
"""
            
            # HTML version
            html = f"""\
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
      <h2 style="color: #2c3e50;">Portfolio Generator</h2>
      <p>Hi {full_name or 'User'},</p>
      <p>Welcome! Your email verification code is:</p>
      
      <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
        <h1 style="color: #3498db; letter-spacing: 5px; margin: 0;">{verification_code}</h1>
      </div>
      
      <p>Please enter this code to complete your account registration.</p>
      <p style="color: #e74c3c; font-size: 14px;">This code will expire in 10 minutes.</p>
      
      <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
      <p style="font-size: 12px; color: #7f8c8d;">
        If you didn't request this code, please ignore this email.
      </p>
      <p style="font-size: 12px; color: #7f8c8d;">
        Best regards,<br>
        Portfolio Generator Team
      </p>
    </div>
  </body>
</html>
"""
            
            # Attach both versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            print(f"✓ Verification email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email: {str(e)}")
            raise Exception(f"Failed to send verification email: {str(e)}")

email_service = EmailService()
