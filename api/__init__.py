"""typing module is mainly used with generic data types, eg, dicts, lists(that have internal types)"""
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel # Python library for data validation

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None # None makes the value optional
    options: list[str] = [] # defaults to an empty list


@app.get("/")
async def read_root():
    return {"success": True, "message": "Welcome to the home page"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None): # str | None=None
    return {"item_id": item_id, "q": q}

@app.put('/items/{item_id}')
async def update_item(item_id: int, item: Item):
    return {"item":item, "item_id": item_id}

# Other parameters in the function that are not in the path parameters are automatically interpreted as query parameters for the request.