import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, dotenv_values
import os

dotenv_path = os.path.join(os.path.dirname(__file__),  '.env')
load_dotenv(dotenv_path)

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
OTP_EMAIL_SUBJECT = os.getenv('OTP_EMAIL_SUBJECT')

# Function to send OTP email
def send_otp_email(receiver_email, otp, session_id):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = receiver_email
        msg['Subject'] = OTP_EMAIL_SUBJECT

        # Email body with OTP
        body = f"Your OTP code for Desuung Attendance Scanner is: {otp}. Do not share with anyone. Valid for 15 minutes"
        msg.attach(MIMEText(body, 'plain'))

        # Create an SMTP session
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Send the email
        server.sendmail(SMTP_USERNAME, receiver_email, msg.as_string())

        # Quit the SMTP server
        server.quit()

        print(f"OTP email sent successfully to {receiver_email}")
        
        return otp  # Return the generated OTP for verification
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")


