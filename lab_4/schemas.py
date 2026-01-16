
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


from pydantic import constr



class HealthResponse(BaseModel):
    status: str
    validationMode: str
    timestamp: str



class UserResponse(BaseModel):
    id: str
    email: str
    role: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class TaskCreate(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=255)

    @validator('title')
    def no_html(cls, v):
        import re
        if re.search(r'<.*?>', v):
            raise ValueError('HTML tags are not allowed in title')
        if '\x00' in v:
            raise ValueError('Null bytes are not allowed in title')
        return v


class TaskUpdate(BaseModel):
    completed: bool


class Task(BaseModel):
    id: str
    title: constr(strip_whitespace=True, min_length=1, max_length=255)
    completed: bool
    user_id: str
    created_at: str



class UserAuth(BaseModel):
    email: EmailStr
    password: str

    class Config:
        extra = "allow"