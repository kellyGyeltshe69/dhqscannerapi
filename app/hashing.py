# Now for hashing pasword or for password encryption 
from passlib.context import CryptContext 

pwt_cxt = CryptContext(schemes=['bcrypt'], deprecated ='auto')

class Hash():
    def bcrypt(password:str):
        return pwt_cxt.hash(password)
    
    
    def verify(plain_password, hashed_password):
        return pwt_cxt.verify(plain_password, hashed_password)