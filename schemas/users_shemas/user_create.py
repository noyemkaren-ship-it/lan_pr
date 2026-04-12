from pydantic import BaseModel

class UserScreateSchema(BaseModel):
    name: str
    email: str
    password: str
