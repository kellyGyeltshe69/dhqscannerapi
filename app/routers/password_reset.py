# # Import necessary libraries and modules
# from fastapi import APIRouter, Depends, HTTPException, Form
# from sqlalchemy.orm import Session
# import random
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.application import MIMEApplication
# from .. import database, schemas, models

# # Create an APIRouter instance
# router = APIRouter()

# # Define a function to generate a random OTP
# def generate_random_otp():
#     return str(random.randint(1000, 9999))

# # Define a function to send an email with OTP
# def send_email(to_email, subject, body):
#     # Email configuration
#     from_email = 'your_email@gmail.com'
#     password = 'your_email_password'
#     smtp_server = 'smtp.gmail.com'
#     smtp_port = 587

#     # Create a MIMEText object for the email body
#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     # Connect to the SMTP server and send the email
#     server = smtplib.SMTP(smtp_server, smtp_port)
#     server.starttls()
#     server.login(from_email, password)
#     server.sendmail(from_email, to_email, msg.as_string())
#     server.quit()

# # Route to initiate password reset and send OTP
# @router.post('/reset-password')
# async def reset_password(
#     user_email: str = Form(...),  # Input the user's email
#     db: Session = Depends(database.get_db)
# ):
#     # Check if the user exists
#     user = db.query(models.User).filter(models.User.email == user_email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')

#     # Generate and send OTP
#     otp = generate_random_otp()
#     subject = 'OTP for Password Reset'
#     body = f'Your OTP for password reset is: {otp}'
#     send_email(user_email, subject, body)

#     # Store the OTP in the database (you may need a separate table for this)
#     db_otp = models.PasswordResetOTP(user_id=user.id, otp=otp)
#     db.add(db_otp)
#     db.commit()

#     return {'message': 'OTP sent successfully'}

# # Route to verify OTP and reset password
# @router.post('/verify-reset-otp')
# async def verify_reset_otp(
#     user_email: str = Form(...),
#     otp: str = Form(...),
#     new_password: str = Form(...),
#     db: Session = Depends(database.get_db)
# ):
#     # Check if the user exists
#     user = db.query(models.User).filter(models.User.email == user_email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')

#     # Check if the OTP is valid
#     db_otp = db.query(models.PasswordResetOTP).filter(
#         models.PasswordResetOTP.user_id == user.id,
#         models.PasswordResetOTP.otp == otp
#     ).first()
#     if not db_otp:
#         raise HTTPException(status_code=400, detail='Invalid OTP')

#     # Update the user's password
#     user.password = hash_password(new_password)  # Implement your password hashing function
#     db.commit()

#     # Delete the used OTP from the database
#     db.delete(db_otp)
#     db.commit()

#     return {'message': 'Password reset successful'}

# # Note: Implement your own password hashing function and adapt this code to your project structure.
