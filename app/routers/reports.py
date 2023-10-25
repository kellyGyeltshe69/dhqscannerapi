from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from datetime import date, timedelta
import csv
from app.database import SessionLocal
from app.models import User, AttendanceRecord, Department
from typing import List
from .. import schemas,oauth2
from ..auth.auth import get_user_role  

router = APIRouter(tags=['Reports'])

# Helper function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to convert a list of dictionaries to a CSV string
def csv_response(data):
    if not data:
        return ""

    # Create a CSV string using the csv module
    csv_string = ','.join(data[0].keys()) + '\n'
    for item in data:
        csv_string += ','.join(map(str, item.values())) + '\n'

    return csv_string

@router.get("/attendance-report", response_model=List[schemas.UserAttendanceReportResponseModel])
async def generate_attendance_report(
    start_date: date = Query(..., description="Start date in yyyy-mm-dd format"),
    end_date: date = Query(..., description="End date in yyyy-mm-dd format"),
    db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    attendance_report = []

    current_date = start_date

    # Create a dictionary to store data by month
    monthly_data = {}

    while current_date <= end_date:
        # Query the database to get attendance records for all users for the current date
        records = db.query(User.cid, User.name, Department.name.label("department"), AttendanceRecord.check_in_date,
                           AttendanceRecord.check_in_time, AttendanceRecord.check_out_time, AttendanceRecord.day_count) \
            .outerjoin(AttendanceRecord, User.id == AttendanceRecord.user_id) \
            .outerjoin(Department, User.department_id == Department.id)  \
            .filter(AttendanceRecord.check_in_date == current_date) \
            .all()

        for cid, name, department, record_date, check_in_time, check_out_time, day_count in records:
            user_data = {
                "cid": cid,
                "name": name,
                "department": department,
                "date": record_date,
                "check_in_time": check_in_time,
                "check_out_time": check_out_time,
                "day_count": day_count,
            }
            attendance_report.append(user_data)

        # Extract the month and year from the current date
        current_month_year = current_date.strftime("%B %Y")

        # Add the data to the corresponding month's data
        if current_month_year not in monthly_data:
            monthly_data[current_month_year] = []

        monthly_data[current_month_year].extend(attendance_report)

        # Clear attendance_report for the next day
        attendance_report = []

        # Move to the next day
        current_date += timedelta(days=1)

    # Generate the CSV content
    csv_monthly = ""
    for month, data in monthly_data.items():
        csv_monthly += f"{month}\n"
        csv_monthly += csv_response(data)
        csv_monthly += "\n"

    # Set up the response
    response = Response(content=csv_monthly)
    response.headers["Content-Disposition"] = 'attachment; filename="attendance_report.csv"'
    response.headers["Content-Type"] = 'text/csv'

    return response


@router.get("/all-attendance", response_model=List[schemas.UserAttendanceReportResponseModel])
async def get_all_attendance_details(
    db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    # Query the database to get all attendance records for all users
    records = db.query(User.cid, User.name, Department.name.label("department"), AttendanceRecord.check_in_date,
                       AttendanceRecord.check_in_time, AttendanceRecord.check_out_time, AttendanceRecord.day_count) \
        .outerjoin(AttendanceRecord, User.id == AttendanceRecord.user_id) \
        .outerjoin(Department, User.department_id == Department.id)  \
        .all()

    attendance_report = []

    for cid, name, department, record_date, check_in_time, check_out_time, day_count in records:
        user_data = {
            "cid": cid,
            "name": name,
            "department": department,
            "date": record_date,
            "check_in_time": check_in_time,
            "check_out_time": check_out_time,
            "day_count": day_count,
        }
        attendance_report.append(user_data)

    # Generate the CSV content
    csv_content = csv_response(attendance_report)

    # Set up the response
    response = Response(content=csv_content)
    response.headers["Content-Disposition"] = 'attachment; filename="attendance_report.csv"'
    response.headers["Content-Type"] = 'text/csv'

    return response
