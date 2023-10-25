# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from .. import database, models,oauth2,schemas
# from ..Enums.enums import UserRole  # Import the UserRole enum

# get_db = database.get_db

# def all(db:Session = Depends(get_db),get_current_user: schemas.users = Depends(oauth2.get_current_user) ):



# rou
# # Example admin-specific endpoint
# @router.get('/api/admin')
# def admin_dashboard(db:Session = Depends(get_db),get_current_user: schemas.users = Depends(oauth2.get_current_user)):
#     """
#     Get admin dashboard information.
#     Only users with the 'admin' role can access this endpoint.
#     """
#     if current_user.role_id != UserRole.ADMIN.value:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource.")
    
#     # You can add your admin-specific logic here
#     admin_dashboard_data = {
#         "message": "Welcome to the admin dashboard!",
#         "admin_info": {
#             "user_id": current_user.id,
#             "username": current_user.cid,
#             # Add more admin-specific data here
#         }
#     }
    
#     return admin_dashboard_data
