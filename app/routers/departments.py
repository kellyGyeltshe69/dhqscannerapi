from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Department
from app.database import SessionLocal
from app import schemas,models,oauth2
from app.auth.auth import get_user_role

router = APIRouter(
    # prefix='/api',
    tags=['Departments'] 
)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
from typing import List

@router.get('/departments_list', response_model=List[str])
def list_departments(db: Session = Depends(get_db),    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    departments = db.query(models.Department.name).all()
    department_names = [name[0] for name in departments]  # Extract the department names
    return department_names

@router.post("/departments/", response_model=schemas.DepartmentResponse)
def create_department(name: str, db: Session = Depends(get_db)):    
    # role_id: int = Depends(get_user_role),
    # current_user: schemas.User = Depends(oauth2.get_current_user)):
    department = Department(name=name)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

@router.get("/departments/{department_id}", response_model=schemas.DepartmentResponse)
def read_department(department_id: int, db: Session = Depends(get_db),    
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    department = db.query(Department).filter(Department.id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.put("/departments/{department_id}", response_model=schemas.DepartmentResponse)
def update_department(department_id: int, name: str, db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    department = db.query(Department).filter(Department.id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    department.name = name
    db.commit()
    db.refresh(department)
    return department

@router.delete("/departments/{department_id}", response_model=schemas.DepartmentResponse)
def delete_department(department_id: int, db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)
    ):
    department = db.query(Department).filter(Department.id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(department)
    db.commit()
    return department
