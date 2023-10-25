from sqlalchemy.orm import Session
from app.models import Department



def create_department(db: Session, name: str):
    department = Department(name=name)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

def read_department(db: Session, department_id: int):
    department = db.query(Department).filter(Department.id == department_id).first()
    return department

def update_department(db: Session, department_id: int, name: str):
    department = db.query(Department).filter(Department.id == department_id).first()
    if department:
        department.name = name
        db.commit()
        db.refresh(department)
    return department

def delete_department(db: Session, department_id: int):
    department = db.query(Department).filter(Department.id == department_id).first()
    if department:
        db.delete(department)
        db.commit()
    return department
