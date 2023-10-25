import os
import io
import qrcode
import base64
from datetime import date
from fastapi import APIRouter,Depends,HTTPException
from PIL import Image
from fastapi.responses import JSONResponse
from app.schemas import QRCodeResponse
from app import schemas,database,oauth2,models
from app.models import DailyToken
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from sqlalchemy.orm import Session



router = APIRouter(
    tags=['QRcode']

)
get_db = database.get_db

def get_user_role(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.cid == current_user.cid).first()
    if user and user.role_id in [1, 4]:  # Roles 1 and 4 are allowed
        return user.role_id
    raise HTTPException(status_code=403, detail="User is not authorized to perform this action")


def generate_and_store_daily_tokens(db):
    try:
        today = date.today()
        check_in_token = f"CHECKIN_{str(today)}"
        check_out_token = f"CHECKOUT_{str(today)}"
    
        print(f"Generated Check-in Token: {check_in_token}")
        print(f"Generated Check-out Token: {check_out_token}")

        existing_record = db.query(DailyToken).filter_by(date=today).first()

        if existing_record:
            # A record for today already exists, you can choose to update it or skip
            # For example, you can update the check-in and check-out tokens
            existing_record.check_in_token = check_in_token
            existing_record.check_out_token = check_out_token
        else:
            # Store both check-in and check-out tokens in the database
            daily_check_in_token = DailyToken(date=today, check_in_token=check_in_token, check_out_token=check_out_token)
            db.add(daily_check_in_token)

        db.commit()
        print("Database commit successful")
    except IntegrityError as e:
        # Handle the IntegrityError
        print(f"IntegrityError: {e}")
        db.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        db.rollback()
    finally:
        db.close()

def generate_check_in_out_qr_codes():
    today = date.today()
    check_in_token = f"CHECKIN_{str(today)}"
    check_out_token = f"CHECKOUT_{str(today)}"

    check_in_qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    check_in_qr.add_data(check_in_token)
    check_in_qr.make(fit=True)

    check_out_qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    check_out_qr.add_data(check_out_token)
    check_out_qr.make(fit=True)

    check_in_bytes = generate_qr_code_bytes(check_in_qr)
    check_out_bytes = generate_qr_code_bytes(check_out_qr)

    check_in_data_url = bytes_to_data_url(check_in_bytes)
    check_out_data_url = bytes_to_data_url(check_out_bytes)

    return check_in_data_url, check_out_data_url

def generate_qr_code_bytes(qr_code):
    img = qr_code.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img = img.convert("RGB")  # Convert the image to RGB mode (required for Pillow)
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# Function to convert bytes to a data URL
def bytes_to_data_url(bytes_data):
    return f"data:image/png;base64,{base64.b64encode(bytes_data).decode()}"

@router.get("/api/qr-codes/{action}", response_model=QRCodeResponse)
async def generate_qr_codes(action: str, role_id: int = Depends(get_user_role),current_user: schemas.User = Depends(oauth2.get_current_user)):
    if action not in ["check-in", "check-out"]:
        return JSONResponse(content={"error": "Invalid action"})

    db = SessionLocal()

    try:
        # Generate and store daily tokens in the database
        generate_and_store_daily_tokens(db)

        check_in_qr_url, check_out_qr_url = generate_check_in_out_qr_codes()
        return JSONResponse(content={"check_in_qr_url": check_in_qr_url, "check_out_qr_url": check_out_qr_url})
    finally:
        db.close()
