from fastapi import Depends, HTTPException, status
from app import JWTtoken,models,database
from fastapi.security import OAuth2PasswordBearer
from app import database
from sqlalchemy.orm import Session

get_db = database.get_db

# This is a route where fastapi will fetch the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = JWTtoken.verify_token(token, credentials_exception)
    
    cid = token_data.cid
    
    user = db.query(models.User).filter(models.User.cid == cid).first()

    return user
