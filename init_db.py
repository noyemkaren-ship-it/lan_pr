from database.base import engine, Base
from models.user_model import User  

Base.metadata.create_all(engine)