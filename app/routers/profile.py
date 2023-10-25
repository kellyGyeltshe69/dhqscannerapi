from fastapi import UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import os
import secrets
from PIL import Image
from fastapi.responses import FileResponse  # Import FileResponse
from app import database, schemas, models, oauth2
from app.repository import profile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

router = APIRouter()
get_db = database.get_db

static_dir = "./app/static" 
router.mount("/static", StaticFiles(directory=static_dir), name="static")

os.makedirs(static_dir, exist_ok=True)

router = APIRouter(tags=['Profile'])

@router.get('/profile', response_model=schemas.UserProfile)
async def get_user_profile(current_user: schemas.User = Depends(oauth2.get_current_user)):
    # Extract department name from the Department object in current_user
    department_name = current_user.department.name if current_user.department else None
    
    user_profile = schemas.UserProfile(
        name=current_user.name,
        department=department_name,
        contact=current_user.contact,
        cid=current_user.cid,
        did=current_user.did,
        email=current_user.email
    )
    return user_profile

@router.put('/update/profile-picture')
async def update_profile_picture_endpoint(
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Get the file extension
    filename, file_extension = os.path.splitext(file.filename)
    
    # Check if the extension is allowed
    allowed_extensions = {'.png', '.jpg', 'jpeg'}
    if file_extension.lower() not in allowed_extensions:
        raise HTTPException(status_code=400, detail='File extension not allowed')

    image_token = secrets.token_hex(10) + file_extension
    generated_name = os.path.join(static_dir, "images", image_token)

    with open(generated_name, 'wb') as image_file:
        image_file.write(file.file.read())

    img = Image.open(generated_name)
    img = img.resize((200, 200))
    img.save(generated_name)

    # Update the user's profile picture URL in the database
    image_url = f"/static/images/{image_token}"
    profile.associate_profile_picture_with_user(db, current_user.cid, image_url)

    return {'status': 'success', 'message': 'Profile picture updated successfully', 'url': image_url}

@router.get('/get/profile-picture/{image_token}')  # New endpoint to serve profile pictures
async def get_profile_picture(image_token: str):
    # Define the path to the image file based on the image_token
    image_path = os.path.join(static_dir, "images", image_token)
    
    # Check if the image file exists
    if os.path.isfile(image_path):
        # Serve the image as a FileResponse
        return FileResponse(image_path, media_type='image/jpeg')  # Adjust the media type as needed
    else:
        raise HTTPException(status_code=404, detail='Image not found')


#  @router.put('/profile')
# async def update_user_profile(
#     updated_profile: schemas.UserUpdate,  # Create a schema for updating user profile fields
#     current_user: schemas.User = Depends(oauth2.get_current_user),
#     db: Session = Depends(database.get_db)
# ):
#     # Update the user's profile information in the database
#     user = db.query(models.User).filter(models.User.cid == current_user.cid).first()
#     if user:
#         for field, value in updated_profile.dict(exclude_unset=True).items():
#             setattr(user, field, value)
#         db.commit()
#     else:
#         raise HTTPException(status_code=404, detail='User not found')

#     return {'status': 'success', 'message': 'Profile updated successfully'}