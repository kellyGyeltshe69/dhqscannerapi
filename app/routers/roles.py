from fastapi import APIRouter
from typing import List
from ..Enums.enums import UserRole

router = APIRouter()

@router.get("/")  
def greeting():
    greet = "Welcome, to all the staff of DHQ"
    return greet

# Create a route to list roles
@router.get("/roles_list", response_model=List[str])  
def get_roles():
    roles = [role.name for role in list(UserRole)] 
    return roles
