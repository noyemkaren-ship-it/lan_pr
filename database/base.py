from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///database.db')

Base = declarative_base()

def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_db():
    return engine, Base, create_session

