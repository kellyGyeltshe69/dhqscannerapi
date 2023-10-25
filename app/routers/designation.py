from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Designation, EmploymentType
from app.database import SessionLocal
from app import schemas,oauth2
from app.auth.auth import get_user_role


router1 = APIRouter(
     tags=['Designation']
)
router2 = APIRouter(
     tags=['Employment Type']
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD operations for Designation
@router1.get('/designations_list', response_model=list[schemas.DesignationResponse])
def list_designations(db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    designations = db.query(Designation).all()
    return designations

@router1.post("/designations/", response_model=schemas.DesignationResponse)
def create_designation(designation: schemas.DesignationCreate, db: Session = Depends(get_db)):
    # role_id: int = Depends(get_user_role),
    # current_user: schemas.User = Depends(oauth2.get_current_user)):
    db_designation = Designation(**designation.dict())
    db.add(db_designation)
    db.commit()
    db.refresh(db_designation)
    return db_designation

@router1.get("/designations/{designation_id}", response_model=schemas.DesignationResponse)
def read_designation(designation_id: int, db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    designation = db.query(Designation).filter(Designation.id == designation_id).first()
    if designation is None:
        raise HTTPException(status_code=404, detail="Designation not found")
    return designation

@router1.put("/designations/{designation_id}", response_model=schemas.DesignationResponse)
def update_designation(designation_id: int, designation: schemas.DesignationUpdate, db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    db_designation = db.query(Designation).filter(Designation.id == designation_id).first()
    
    if db_designation is None:
        raise HTTPException(status_code=404, detail="Designation not found")
    for key, value in designation.dict().items():
        setattr(db_designation, key, value)
    db.commit()
    db.refresh(db_designation)
    return db_designation

@router1.delete("/designations/{designation_id}", response_model=schemas.DesignationResponse)
def delete_designation(designation_id: int, db: Session = Depends(get_db),   
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    designation = db.query(Designation).filter(Designation.id == designation_id).first()
    if designation is None:
        raise HTTPException(status_code=404, detail="Designation not found")
    db.delete(designation)
    db.commit()
    return designation

# CRUD operations for Employment Type
@router2.get('/employment_types_list', response_model=list[schemas.EmploymentTypeResponse])
def list_employment_types(db: Session = Depends(get_db),    
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    employment_types = db.query(EmploymentType).all()
    return employment_types

@router2.post("/employment_types/", response_model=schemas.EmploymentTypeResponse)
def create_employment_type(employment_type: schemas.EmploymentTypeCreate, db: Session = Depends(get_db)):
    # role_id: int = Depends(get_user_role),
    # current_user: schemas.User = Depends(oauth2.get_current_user)):
    db_employment_type = EmploymentType(**employment_type.dict())
    db.add(db_employment_type)
    db.commit()
    db.refresh(db_employment_type)
    return db_employment_type

@router2.get("/employment_types/{employment_type_id}", response_model=schemas.EmploymentTypeResponse)
def read_employment_type(employment_type_id: int, db: Session = Depends(get_db),    
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    employment_type = db.query(EmploymentType).filter(EmploymentType.id == employment_type_id).first()
    if employment_type is None:
        raise HTTPException(status_code=404, detail="Employment Type not found")
    return employment_type

@router2.put("/employment_types/{employment_type_id}", response_model=schemas.EmploymentTypeResponse)
def update_employment_type(employment_type_id: int, employment_type: schemas.EmploymentTypeUpdate, db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    db_employment_type = db.query(EmploymentType).filter(EmploymentType.id == employment_type_id).first()
    if db_employment_type is None:
        raise HTTPException(status_code=404, detail="Employment Type not found")
    for key, value in employment_type.dict().items():
        setattr(db_employment_type, key, value)
    db.commit()
    db.refresh(db_employment_type)
    return db_employment_type

@router2.delete("/employment_types/{employment_type_id}", response_model=schemas.EmploymentTypeResponse)
def delete_employment_type(employment_type_id: int, db: Session = Depends(get_db),   
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    employment_type = db.query(EmploymentType).filter(EmploymentType.id == employment_type_id).first()
    if employment_type is None:
        raise HTTPException(status_code=404, detail="Employment Type not found")
    db.delete(employment_type)
    db.commit()
    return employment_type
