from fastapi import UploadFile, File, Depends, HTTPException,APIRouter
from sqlalchemy.orm import Session
import os
import secrets
from PIL import Image
from app import database, schemas, models, oauth2  # Adjust your import paths as needed
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


router = APIRouter()
get_db = database.get_db



def associate_profile_picture_with_user(db: Session, user_id: int, profile_picture_filename: str):
    user = db.query(models.User).filter(models.User.cid == user_id).first()
    if user:
        user.avatar = profile_picture_filename
        db.commit()

async def get_current_user(token: str = Depends(oauth2.oauth2_scheme)):
    return oauth2.get_current_user(token) 