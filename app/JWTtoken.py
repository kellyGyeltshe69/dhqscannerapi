from datetime import datetime, timedelta
from jose import JWTError, jwt
from app import schemas
from dotenv import load_dotenv, dotenv_values
import os

dotenv_path = os.path.join(os.path.dirname(__file__),  '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))



def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated Token: {encoded_jwt}")
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cid = payload.get("sub")
        if cid is None:
            raise JWTError(description="Token payload does not contain 'sub'")
        token_data = schemas.TokenData(cid=cid)
        return token_data
    except JWTError as e:
        # print(f"JWT Error: {e}")
        raise credentials_exception
