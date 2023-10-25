from fastapi import Depends, HTTPException, Response, APIRouter, status
from sqlalchemy.orm import Session
from app import database, schemas, models, oauth2
from app.repository import user
from fastapi.responses import JSONResponse
from fastapi import Depends, File, UploadFile, APIRouter
from sqlalchemy.orm import Session
import io
import csv
from app import models, schemas, database, oauth2
from fastapi import HTTPException, status
from app.hashing import Hash

get_db = database.get_db

router = APIRouter(
    prefix='/user',
    tags=['Users']    
)



@router.post('/', response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    existing_user_with_cid = db.query(models.User).filter(models.User.cid == request.cid).first()
    if existing_user_with_cid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CID {request.cid} is already in use")

    existing_user_with_did = db.query(models.User).filter(models.User.did == request.did).first()
    if existing_user_with_did:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"DID {request.did} is already in use")

    department_name = request.department
    designation_name = request.designation
    employment_type_name = request.employment_type
    print(f"Received names: Department={department_name}, Designation={designation_name}, EmploymentType={employment_type_name}")


    department = db.query(models.Department).filter(models.Department.name == department_name).first()
    designation = db.query(models.Designation).filter(models.Designation.name == designation_name).first()
    employment_type = db.query(models.EmploymentType).filter(models.EmploymentType.name == employment_type_name).first()
    print(f"Related entities: Department={department}, Designation={designation}, EmploymentType={employment_type}")


    if not department or not designation or not employment_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more related entities do not exist.")

    new_user = models.User(
        name=request.name,
        did=request.did,
        email=request.email,
        contact=request.contact,
        password=Hash.bcrypt(request.password),
        cid=request.cid,
        role_id=request.role_id,
        department=department,  # Assign the related Department object
        designation=designation,  # Assign the related Designation object
        employment_type=employment_type  # Assign the related EmploymentType object
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "name": new_user.name,
        "contact": new_user.contact,
        "cid": new_user.cid,
        "role_id": new_user.role_id,
        "department": department_name,
        "designation": designation_name,
        "employment_type": employment_type_name
    }



def get_user_by_cid(cid: int, db: Session):
    return db.query(models.User).filter(models.User.cid == cid).first()

def update_user(user: models.User, user_update:schemas.UserUpdate, db: Session):
    for field, value in user_update.dict().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(existing_user: models.User, db: Session):
    db.delete(existing_user)
    db.commit()
    return existing_user