from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    completed: bool


class Task(BaseModel):
    id: str
    title: str
    completed: bool
    created_at: datetime


class UserAuth(BaseModel):
    email: EmailStr
    password: str