from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, text, Date, Time,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from app.Enums.enums import  UserRole  # Make sure to import your enum types here
from app.database import SessionLocal


Base = declarative_base()

# Role model
class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    # Define the reverse relationship to User
    users = relationship("User", back_populates="role")  # Add this line
    
def init_db():
    # Insert predefined roles if they don't exist
    session = SessionLocal()
    try:
        for role_id, role_name in [(1, "admin"), (2, "hr"), (3, "staff"), (4, "qrGenerate")]:
            role = session.query(Role).filter(Role.id == role_id).first()
            if role is None:
                role = Role(id=role_id, name=role_name)
                session.add(role)
        session.commit()
    finally:
        session.close()

# User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    did = Column(String)
    email = Column(String)
    contact = Column(Integer)
    password = Column(String)
    cid = Column(Integer)
    department_id = Column(Integer, ForeignKey("departments.id")) 
    designation_id = Column(Integer, ForeignKey('designations.id'))
    employment_type_id = Column(Integer, ForeignKey('employment_types.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))
    is_active = Column(Boolean, default=True)
    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
    attendance_records = relationship("AttendanceRecord", back_populates="user")
    designation = relationship("Designation", back_populates="users", primaryjoin="User.designation_id == Designation.id")
    employment_type = relationship("EmploymentType", back_populates="users", primaryjoin="User.employment_type_id == EmploymentType.id")
    
    
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="department")
    
class Designation(Base):
    __tablename__ = 'designations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="designation")

class EmploymentType(Base):
    __tablename__ = 'employment_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="employment_type")
    


# AttendanceRecord model
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    user_role = Column(String, index=True)  # Use String type for Python Enum
    check_in_date = Column(Date)
    check_in_time = Column(Time)
    check_out_date = Column(Date)
    check_out_time = Column(Time)
    day_count = Column(Integer, default=0) 

    user_id = Column(Integer, ForeignKey('users.id'))

    # Establish a many-to-one relationship with User
    user = relationship("User", back_populates="attendance_records")


class DailyToken(Base):
    __tablename__ = "daily_tokens"  # Name of the database table

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)  # Date for which the token is valid
    check_in_token = Column(String, unique=True)  # Unique check-in token for the day
    check_out_token = Column(String, unique=True)
    
    
    
class Otp(Base):
    __tablename__ = 'otp'
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(String(100))
    session_id = Column(String(36)) 
    otp_code = Column(String)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    otp_failed_count = Column(Integer, default=0)
    