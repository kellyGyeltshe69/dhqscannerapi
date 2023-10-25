from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, database, models, JWTtoken
from sqlalchemy.orm import Session
from app.hashing import Hash
from fastapi.security import OAuth2PasswordRequestForm
from app.Enums.enums import UserRole  # Import the UserRole enum

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.cid == request.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")

    if user.role_id == UserRole.ADMIN.value:
        redirect_url = "/api/admin" 
        
    elif user.role_id == UserRole.HR.value:
        redirect_url = "/api/hr" 

    elif user.role_id == UserRole.STAFF.value:
        redirect_url = "/api/staff" 
        
    elif user.role_id == UserRole.QRGENERATOR.value:
        redirect_url = "/api/qr-codes"  
         
    else:
        redirect_url = None 

    access_token = JWTtoken.create_access_token(data={"sub": str(user.cid)}) 

    return {"access_token": access_token,"token_type": "bearer","redirect_url": redirect_url,"userRole": user.role.name 
}
