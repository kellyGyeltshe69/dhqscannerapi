import secrets
import string
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import models, database, schemas
from app.Emailotp import send_otp_email
from app.hashing import Hash
from dotenv import dotenv_values

# Load environment variables from .env file
env_variables = dotenv_values('.env')

# Define the maximum number of OTP attempts (default to 5 if not found in .env)
MAX_OTP_ATTEMPTS = int(env_variables.get('MAX_OTP_ATTEMPTS', 5))

# Create a FastAPI router
router = APIRouter(
    tags=['otp']

)

# Function to generate a random OTP
def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(secrets.choice(characters) for _ in range(length))
    return otp

@router.post('/forgot-password')
# async def forgot_password(cid: int, db: Session = Depends(database.get_db)):
async def forgot_password(request_data: schemas.CIDRequest, db: Session = Depends(database.get_db)):
    cid = request_data.cid

    # Check if the user with the provided CID exists in the database
    user = db.query(models.User).filter(models.User.cid == cid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if the user has a valid email address
    if not user.email or "@" not in user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have a valid email address, Contact your adminstrator")

    # Generate a random OTP
    otp = generate_otp()  # Generate OTP once

    # Generate a unique session_id (UUID)
    session_id = str(uuid.uuid4())  # Generate a UUID

    # Store the OTP, recipient_id (user's email), session_id, and timestamp in the database
    otp_data = models.Otp(
        recipient_id=user.email,
        otp_code=otp,
        session_id=session_id,
        created_on=datetime.utcnow()
    )
    db.add(otp_data)
    db.commit()

    # Send the OTP and session_id via email
    send_otp_email(user.email, otp, session_id)  # Use the same OTP generated above

    return {"message": "OTP sent successfully"}




@router.post('/enter-otp')
async def enter_otp_and_set_password(cid: int, verify_otp: schemas.VerifyOTP, db: Session = Depends(database.get_db)):
    # Check if the user with the provided CID exists in the database
    user = db.query(models.User).filter(models.User.cid == cid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Fetch the associated email address for the user
    email = user.email

    # Check if the entered OTP is correct
    otp_data = db.query(models.Otp).filter(
        models.Otp.recipient_id == email,
        models.Otp.otp_code == verify_otp.otp_code,
        models.Otp.otp_failed_count < MAX_OTP_ATTEMPTS
    ).order_by(models.Otp.created_on.desc()).first()

    if not otp_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP or OTP expired")

    # Return a success message indicating that the OTP is correct
    return {"message": "You have successfully entered the correct OTP"}



from datetime import datetime, timedelta
from ..schemas import VerifyOTP, ResetPassword


# Modify the /reset-password endpoint to accept the OTP code in the request body
@router.post('/reset-password')
async def reset_password(reset_data: schemas.ResetPassword, db: Session = Depends(database.get_db)):
    # Check if the OTP provided by the user is valid
    otp_data = db.query(models.Otp).filter(
        models.Otp.otp_code == reset_data.otp_code,  # Change this line
        models.Otp.otp_failed_count < MAX_OTP_ATTEMPTS
    ).order_by(models.Otp.created_on.desc()).first()

    if not otp_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP or OTP expired")

    # Check OTP expiration
    current_time = datetime.utcnow()
    otp_creation_time = otp_data.created_on
    otp_expiration_minutes = int(env_variables.get('OTP_EXPIRATION_MINUTES', 15))
    otp_expiration_time = otp_creation_time + timedelta(minutes=otp_expiration_minutes)

    if current_time > otp_expiration_time:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP has expired")

    # Retrieve recipient_id and session_id from the OTP data
    recipient_id = otp_data.recipient_id
    session_id = otp_data.session_id

    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    # Update the user's password (you need to implement a password hashing function)
    new_password_hashed = Hash.bcrypt(reset_data.new_password)
    user = db.query(models.User).filter(models.User.email == recipient_id).first()
    user.password = new_password_hashed
    db.delete(otp_data)  # Remove the used OTP record
    db.commit()

    return {"message": "Password reset successfully"}

