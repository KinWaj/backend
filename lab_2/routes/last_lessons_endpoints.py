from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from auth import get_current_user

router = APIRouter(tags=['lessons'])

class Item(BaseModel):
    name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Element 3"
            }
        }

class ItemWithDescription(BaseModel):
    name: str
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "New element",
                "description": "New description"
            }
        }


data = [
    {"id": 1, "name": "Element 1"},
    {"id": 2, "name": "Element 2"}
]


items = [
    {"id": 1, "name": "Element 1", "description": "description 1"},
    {"id": 2, "name": "Element 2", "description": "description 2"}
]

@router.get(
    "/health",
    responses={
        200: {
            "description": "Health check response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "timestamp": "2024-01-15T10:30:00.123456"
                    }
                }
            }
        }
    }
)
def get_health():
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat()
    }

@router.get(
    "/data",
    responses={
        200: {
            "description": "List of all data items",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 1, "name": "Element 1"},
                        {"id": 2, "name": "Element 2"}
                    ]
                }
            }
        }
    }
)
def get_data(user=Depends(get_current_user)):
    """Get all data - available for all authenticated users"""
    return data

@router.get(
    "/items",
    responses={
        200: {
            "description": "List of all items with descriptions",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 1, "name": "Element 1", "description": "Opis"},
                        {"id": 2, "name": "Element 2", "description": "Opis"}
                    ]
                }
            }
        }
    }
)
def get_items(user=Depends(get_current_user)):
    return items

@router.post(
    "/items",
    responses={
        200: {
            "description": "Successfully added item with description",
            "content": {
                "application/json": {
                    "example": {
                        "id": 3,
                        "name": "Nowy element",
                        "description": "Nowy opis"
                    }
                }
            }
        }
    }
)
def add_item(item: ItemWithDescription, user=Depends(get_current_user)):
    new_item = {
        "id": len(items) + 1,
        "name": item.name,
        "description": item.description
    }
    items.append(new_item)
    return new_item

@router.post(
    "/data",
    responses={
        200: {
            "description": "Successfully added item",
            "content": {
                "application/json": {
                    "example": {
                        "id": 3,
                        "name": "Element 3"
                    }
                }
            }
        }
    }
)
def add_data(item: Item, user=Depends(get_current_user)):
    """Add new data item - available for all authenticated users"""
    new_item = {
        "id": len(data) + 1,
        "name": item.name
    }
    data.append(new_item)
    return new_item
