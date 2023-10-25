from Enums.enums import DepartmentEnum
import pdb
from sqlalchemy import Enum, Column, text
from sqlalchemy.ext.declarative import declarative_base
# pdb.set_trace()
print(type(DepartmentEnum))

Base = declarative_base()

# Rest of your SQLAlchemy model and code...
