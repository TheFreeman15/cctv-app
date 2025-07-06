from pydantic import BaseModel, Field,EmailStr,model_validator
from typing import Optional



class UserLogin(BaseModel):
    email: EmailStr = Field(min_length=1,default="user@gmail.com")
    password: Optional[str] = Field(min_length=1, default="UserPassword")
    refresh_token: Optional[str] = Field(min_length=1, default=None)

    @model_validator(mode='before')
    @classmethod
    def validate(cls,values):
        if not values.get('password') and not values.get('refresh_token'):
            raise ValueError("Either password or refresh_token must be provided")
        return values

class CreateUser(BaseModel):
    user_name: str = Field(min_length=1, default="UserName")
    user_email: EmailStr = Field(min_length=1, default="admin@gmail.com")
    role: str = Field(min_length=1, default="supervisor")
    password: str= Field(min_length=1, default="UserPassword")

class ModifyUser(BaseModel):
    user_email: EmailStr = Field(min_length=1,default="user@gmail.com")
    user_name: str = Field(min_length=1, default=None)
    role: Optional[str] = Field(min_length=1, default="supervisor")
    password: Optional[str] = Field(min_length=1, default="UserPassword")
    

class DeleteUser(BaseModel):
    # Add a sample value in below fields
    user_email: EmailStr = Field(min_length=1, default="user@gmail.com")

class CreateCamera(BaseModel):
    device_name: str = Field(min_length=1,default="camera-name")
    device_ip: str = Field(min_length=1,default="192.168.1.12")
    device_location: str = Field(min_length=1, default="hallway")

class AssignCamera(BaseModel):
    device_name: str = Field(min_length=1,default="camera-name")
    user_email: EmailStr = Field(min_length=1, default="user@gmail.com")

class DeleteCamera(BaseModel):
    device_name: str = Field(min_length=1,default="camera-name")

class ModifyCamera(BaseModel):
    device_name: str = Field(min_length=1,default="camera-name")
    new_device_name: Optional[str] = Field(min_length=1, default=None)
    new_device_ip: Optional[str] = Field(min_length=1, default=None)
    new_device_location: Optional[str] = Field(min_length=1, default=None)

class DeassignCamera(BaseModel):
    device_name: str = Field(min_length=1,default="camera-name")
    user_email: EmailStr = Field(min_length=1, default="user@gmail.com")