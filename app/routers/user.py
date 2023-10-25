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

def get_user_role(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.cid == current_user.cid).first()
    if user and user.role_id in [1, 2]: 
        return user.role_id
    raise HTTPException(status_code=403, detail="User is not authorized to perform this action")

def get_department_name_by_id(department_id: int, db: Session):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if department:
        return department.name
    return None


def convert_active_status(is_active: bool) -> str:
    return "active" if is_active else "inactive"



@router.post('/', response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
                # role_id: int = Depends(get_user_role) , 
                # current_user: schemas.User = Depends(oauth2.get_current_user)):
    user_data = user.create_user(request, db)
    user_data_with_is_active = {**user_data, "is_active": 'active'} 
    return user_data_with_is_active



@router.get("/{cid}", response_model=schemas.UserRead)
def read_user(cid: int, db: Session = Depends(get_db)):
    user_data = user.get_user_by_cid(cid, db)
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    is_active = 'active' if user_data.is_active else 'inactive'

    user_read = schemas.UserRead(
        name=user_data.name,
        contact=user_data.contact,
        cid=user_data.cid,
        is_active=is_active,
        department=user_data.department.name,
        role_id=user_data.role_id,
        designation_id=user_data.designation_id,
        employment_type_id=user_data.employment_type_id,
        did=user_data.did,  # Include 'did' field
        email=user_data.email  # Include 'email' field
    )
    return user_read


@router.get("/{cid}", response_model=schemas.UserRead)
def get_user_by_cid(cid: int, db: Session = Depends(get_db)):
    user_data = user.get_user_by_cid(cid, db)
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    is_active = 'active' if user_data.is_active else 'inactive'

    user_read = schemas.UserRead(
        name=user_data.name,
        contact=user_data.contact,
        cid=user_data.cid,
        is_active=is_active,
        department=user_data.department.name,
        role_id=user_data.role_id,
        designation_id=user_data.designation_id,
        employment_type_id=user_data.employment_type_id,
        did=user_data.did,  # Include 'did' field
        email=user_data.email  # Include 'email' field
    )
    return user_read

@router.put("/{cid}", response_model=schemas.ShowUser)
def update_user_by_cid(cid: int, request: schemas.UserUpdate, db: Session = Depends(get_db)):
    user_data = user.get_user_by_cid(cid, db)

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user data
    # ...

    is_active = convert_active_status(user_data.is_active)

    updated_user = schemas.ShowUser(
        # Define your fields here
        name=user_data.name,
        did=user_data.did,
        email=user_data.email,
        contact=user_data.contact,
        cid=user_data.cid,
        department=user_data.department.name,
        role_id=user_data.role_id,
        designation_id=user_data.designation_id,
        employment_type_id=user_data.employment_type_id,
        is_active=is_active
    )

    return updated_user










@router.delete("/{cid}", response_model=schemas.UserDelete)
def delete_user(cid: int, db: Session = Depends(get_db)):
    user_data = user.get_user_by_cid(cid, db)
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = user.delete_user(user_data, db)
    return deleted_user


def process_csv(file_contents, db, department_id):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    decoded_file = file_contents.decode('utf-8', errors='ignore')
    csv_data = csv.DictReader(io.StringIO(decoded_file), delimiter=',')

    created_users = []

    for row in csv_data:
        new_user = models.User(
            name = row.get('name').strip(),
            did=row['did'].strip(),
            email=row['email'].strip(),
            contact=row['contact'].strip(),
            password=Hash.bcrypt(row['cid'].strip()),
            cid=row['cid'].strip(),
            role_id=row['role_id'].strip(),
            department=department
        )

        existing_user_with_cid = db.query(models.User).filter(models.User.cid == new_user.cid).first()
        existing_user_with_did = db.query(models.User).filter(models.User.did == new_user.did).first()

        if existing_user_with_cid or existing_user_with_did:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CID or DID already in use")

        db.add(new_user)
        created_users.append(new_user)

    db.commit()
    return created_users


@router.post('/bulk', response_model=list[schemas.ShowUser])
def create_bulk_users(
    department_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
   
    department = db.query(models.Department).filter(models.Department.name == department_name).first()
    if not department:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Department {department_name} does not exist")
    created_users = process_csv(file.file.read(), db, department.id)
    
    for user in created_users:
        user.is_active = 'active' if user.is_active else 'inactive'
    return created_users



@router.put('/activate/{cid}', response_model=schemas.ShowUser)
def activate_user_by_cid(cid: int, db: Session = Depends(get_db),   
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    user_to_activate = db.query(models.User).filter(models.User.cid == cid).first()

    if not user_to_activate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with CID {cid} not found")

    user_to_activate.is_active = 1
    db.commit()

    user_to_activate.is_active = 'active'

    return user_to_activate

@router.put('/deactivate/{cid}', response_model=schemas.ShowUser)
def deactivate_user_by_cid(cid: int, db: Session = Depends(get_db),
    role_id: int = Depends(get_user_role),
    current_user: schemas.User = Depends(oauth2.get_current_user)):
    user_to_deactivate = db.query(models.User).filter(models.User.cid == cid).first()

    if not user_to_deactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with CID {cid} not found")

    user_to_deactivate.is_active = 0
    db.commit()

    user_to_deactivate.is_active = 'inactive'

    return user_to_deactivate
