from fastapi import FastAPI, HTTPException,Depends,APIRouter
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from ..import schemas,database,models,JWTtoken
from typing import List
from app.database import SessionLocal
from app.models import User, AttendanceRecord

router = APIRouter()


get_db = database.get_db


def mark_usesr_present(scanned_token):
    db = SessionLocal()
    
    user = db.query(User).filter_by(qr_code_token=scanned_token).first()

    if user:
        # Create an attendance record and increment attendance count
        attendance_record = AttendanceRecord(user_id=user.id)
        user.attendance_count += 1  # Increment the attendance count
        db.add(attendance_record)
        db.commit()
        db.close()
        return True  # User marked as present and attendance incremented
    else:
        db.close()
        return False  # Scanned token not found or invalid



