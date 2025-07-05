from pydantic import BaseModel, Field
from typing import Optional



class UserLogin(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)

class CreateUser(BaseModel):
    #TODO: EMail validators ???
    user_name: str = Field(min_length=1)
    user_email: str = Field(min_length=1)
    role: str = Field(min_length=1)
    password: str= Field(min_length=1)

class ModifyUser(BaseModel):
    user_email: str = Field(min_length=1) # Only attribute that cannot be modified
    user_name: str = Field(min_length=1, default=None)
    role: Optional[str] = Field(default=None, min_length=1)
    password: Optional[str] = Field(default=None, min_length=1)
    

class DeleteUser(BaseModel):
    user_email: str = Field(min_length=1)

class CreateCamera(BaseModel):
    device_name: str = Field(min_length=1)
    device_ip: str = Field(min_length=1)
    device_location: str = Field(min_length=1)