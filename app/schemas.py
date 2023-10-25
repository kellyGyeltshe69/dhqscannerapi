from pydantic import BaseModel
from typing import List
# from sqlalchemy.ext.declarative import declarative_base
from .Enums.enums import  UserRole
from typing import Optional


class UserProfile(BaseModel):
    name: str
    contact:int
    cid: int
    did:str
    email:str
    department: str

 

class User(BaseModel):
    name: str
    did: str
    email: str
    contact: int
    password: str
    cid: int
    department: str  # You can use str for the department name
    role_id: int = 3
    designation: str  # Use str for the designation name
    employment_type: str 

    
    class Config():
        orm_mode = True
        
        
class UserUpdate(BaseModel):
    name: Optional[str]
    did: Optional[str]
    email: Optional[str]
    contact: Optional[int]
    password: Optional[str]
    role_id: Optional[int]
    designation_id: Optional[int]
    employment_type_id: Optional[int]
    is_active: str


class UserRead(BaseModel):
    name: str
    did: str
    email: str
    contact: int
    cid: int
    department: str
    role_id: int
    designation_id: int
    employment_type_id: int
    is_active: str

class UserDelete(BaseModel):
    cid: int

class ShowUser(BaseModel):
    name:str
    contact:int
    cid:int
    is_active: str 
  
    class Config():
        orm_mode = True



class QRCodeResponse(BaseModel):
    check_in_qr_url: str
    check_out_qr_url: str
    
    
class ScannedData(BaseModel):
    token: str
    class Config:
        orm_mode = True
        
        
class TokenData(BaseModel):
    cid:int


class CreateOTP(BaseModel):
    recipient_id:str
    
class VerifyOTP(BaseModel):
    otp_code: str
    
class ResetPassword(BaseModel):
    otp_code: str
    new_password: str  
    confirm_password:str
    
class OTPList(VerifyOTP):
    otp_failed_count:int
    
    
class CIDRequest(BaseModel):
    cid: int
    
from datetime import date, time

    
class UserAttendanceReportResponseModel(BaseModel):
    cid: int
    name: str
    department: str
    date: date
    check_in_time: time
    check_out_time: time
    day_count: int  # Add day_count to the response model


class Department(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        
        
class DepartmentResponse(BaseModel):
    id: int
    name: str
    
class DepartmentCreate(BaseModel):
    name: str

class DepartmentUpdate(BaseModel):
    name: Optional[str]

    
class DesignationBase(BaseModel):
    name: str

class DesignationCreate(DesignationBase):
    pass

class DesignationResponse(DesignationBase):
    id: int

class DesignationUpdate(DesignationBase):
    pass

class EmploymentTypeBase(BaseModel):
    name: str

class EmploymentTypeCreate(EmploymentTypeBase):
    pass

class EmploymentTypeResponse(EmploymentTypeBase):
    id: int

class EmploymentTypeUpdate(EmploymentTypeBase):
    pass
