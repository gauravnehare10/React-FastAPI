from pydantic import BaseModel

class User(BaseModel):
    name: str
    username: str
    email: str
    contactnumber: int
    password: str

    
