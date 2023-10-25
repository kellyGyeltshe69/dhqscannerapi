from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import models 
from app.database import get_db
from app.oauth2 import get_current_user

def get_user_role(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.cid == current_user.cid).first()
    if user and user.role_id in [1, 2]:  # Roles 1 (admin) and 2 (hr)
        return user.role_id
    raise HTTPException(status_code=403, detail="User is not authorized to perform this action")
