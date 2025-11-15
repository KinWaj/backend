"""
Simple REST API created as an example for learning backend development.

This project demonstrates basic CRUD operations using FastAPI framework 
with in-memory data storage. The API includes endpoints for managing data 
items and provides interactive Swagger documentation for easy testing.

Endpoints:
    - GET /health: Health check endpoint
    - GET /data: Retrieve all data items
    - POST /data: Add a new data item
    - GET /items: Retrieve all items with descriptions
    - POST /items: Add a new item with description
"""

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Model danych
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

# Dane w pamięci
data = [
    {"id": 1, "name": "Element 1"},
    {"id": 2, "name": "Element 2"}
]

# Items z opisami
items = [
    {"id": 1, "name": "Element 1", "description": "description 1"},
    {"id": 2, "name": "Element 2", "description": "description 2"}
]

@app.get(
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

@app.get(
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
def get_data():
    return data

@app.get(
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
def get_items():
    return items

@app.post(
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
def add_item(item: ItemWithDescription):
    new_item = {
        "id": len(items) + 1,
        "name": item.name,
        "description": item.description
    }
    items.append(new_item)
    return new_item

@app.post(
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
def add_data(item: Item):
    new_item = {
        "id": len(data) + 1,
        "name": item.name
    }
    data.append(new_item)
    return new_item