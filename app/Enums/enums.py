from enum import Enum
from fastapi import HTTPException

class UserRole(Enum):
    ADMIN = 1
    HR = 2
    STAFF = 3
    QRGENERATOR = 4
