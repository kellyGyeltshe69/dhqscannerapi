from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from app import schemas, database,oauth2
from app.models import User, AttendanceRecord
from app.routers.qr_generator import generate_check_in_out_qr_codes, DailyToken

router = APIRouter(
    tags=['QRcode']

)

get_db = database.get_db

# Generate QR codes and store them in variables
check_in_qr_url, check_out_qr_url = generate_check_in_out_qr_codes()

# Use a dictionary to keep track of check-in and check-out statuses for each user
user_check_in_status = {}
user_check_out_status = {}

@router.post("/api/qr-scan")
async def handle_qr_scan(scanned_data: dict, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    global last_scanned_action  # Use a global variable to track the last scanned action

    cid = scanned_data.get("cid")
    token = scanned_data.get("token")

    if not cid or not token:
        raise HTTPException(status_code=400, detail="Invalid scanned data")

    user = db.query(User).filter(User.cid == cid).first()

    if user:
        current_date = date.today()
        current_time = datetime.now().time()

        has_checked_in_today = any(
            record.check_in_date == current_date for record in user.attendance_records
        )

        has_checked_out_today = any(
            record.check_out_date == current_date for record in user.attendance_records
        )

        # Initialize check-in and check-out statuses for this user if not already present
        user_check_in_status.setdefault(cid, False)
        user_check_out_status.setdefault(cid, False)

        if user_check_in_status.get(cid, False) and "CHECKIN" in token:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="You have already checked-in. Thank You!",
            )

        daily_token = db.query(DailyToken).filter(
            DailyToken.date == current_date
        ).first()

        if not daily_token:
            raise HTTPException(status_code=400, detail="No valid daily token found")

        if "CHECKIN" in token:
            if not has_checked_in_today:
                if not token.startswith("CHECKIN_"):
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Invalid QR Code format for check in.",
                    )
                if token != daily_token.check_in_token:  # Check against check_in_token
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Invalid token for the current check in status",
                    )
                # User hasn't checked in yet today, create a new record for check-in
                check_in_time = current_time.strftime("%I:%M %p")  # Format time as 12-hour
                check_in_time_obj = datetime.strptime(check_in_time, "%I:%M %p").time()
                attendance_record = AttendanceRecord(
                    user_role=user.role.name,
                    check_in_date=current_date,
                    check_in_time=check_in_time_obj,
                    user_id=user.id,
                    day_count=0,
                )
                db.add(attendance_record)
                last_scanned_action = "check-in"  # Update the last scanned action

                user_check_in_status[cid] = True  # Mark check-in status as True
                
                db.commit()

                # Get the total day count for the user
                total_day_count = sum(
                    record.day_count for record in user.attendance_records
                )

                return {
                    "message": "You have successfully checked in.",  # Success message for check-in
                    "day_count": total_day_count,
                    "check_in_qr_url": check_in_qr_url,
                    "check_out_qr_url": check_out_qr_url,
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="You have already checked-in. Thank You!",
                )
        elif "CHECKOUT" in token:
            if not has_checked_in_today:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="You must Check-in before checking out!",
                )
            if user_check_out_status[cid]:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="You have already checked out today. Thank You!",
                )
            if user_check_in_status[cid]:
                if not token.startswith("CHECKOUT_"):
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Invalid QR Code format for check-out.",
                    )
                if token != daily_token.check_out_token:  # Check against check_out_token
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Invalid QR Code! Try again!",
                    )
                # User has checked in today but not checked out, update the existing check-in record
                for record in user.attendance_records:
                    if (
                        record.check_out_date is None
                        and record.check_in_date == current_date
                    ):
                        check_out_time = current_time.strftime("%I:%M %p")  # Format time as 12-hour
                        check_out_time_obj = datetime.strptime(check_out_time, "%I:%M %p").time()
                        record.check_out_date = current_date
                        record.check_out_time = check_out_time_obj  # Store as time object
                        record.day_count += 1
                        last_scanned_action = "check-out"  # Update the last scanned action
                        user_check_out_status[cid] = True  # Mark check-out status as True
                        
                        db.commit()

                        # Get the total day count for the user
                        total_day_count = sum(
                            record.day_count for record in user.attendance_records
                        )

                        return {
                            "message": "You have successfully checked out.",  # Success message for check-out
                            "day_count": total_day_count,
                            "check_in_qr_url": check_in_qr_url,
                            "check_out_qr_url": check_out_qr_url,
                        }
                # If no matching check-in record is found, handle this as an error
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No matching check-in record found for check-out.",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="Please Check-in before checking out!",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Invalid Qrcode",
            )

    else:
        raise HTTPException(status_code=404, detail="User not found")
