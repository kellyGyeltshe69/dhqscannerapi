from fastapi import FastAPI,UploadFile,Depends
from app import models,schemas
from app.database import engine
from app.routers import  user,qr_generator,record_attendance,qr_Scanner,profile,reports,reset_passwd,departments,roles,designation
from app.auth import authentication
from app import fetchExternalApi
from app.models import init_db  
from dotenv import dotenv_values



app = FastAPI() 


app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(qr_generator.router)
app.include_router(record_attendance.router)  
app.include_router(qr_Scanner.router)
app.include_router(profile.router)
app.include_router(reports.router)
app.include_router(reset_passwd.router)
app.include_router(departments.router)
app.include_router(roles.router)
app.include_router(designation.router1)  # Assuming you have router1 defined elsewhere
app.include_router(designation.router2)
app.include_router(fetchExternalApi.router)

env_variables = dotenv_values('.env')




models.Base.metadata.create_all(engine)  

init_db()

