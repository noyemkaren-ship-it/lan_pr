from pydantic import BaseModel

class UserGetSchemasByName(BaseModel):
    name: str
    
class UserGetSchemasById(BaseModel):
    id: int
    
    
class UserGetSchemasByNameAndPassword(BaseModel):
    name: str
    password: str
    