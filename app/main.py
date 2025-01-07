import django
from django.conf import settings
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from django.core.wsgi import get_wsgi_application
from typing import List
from pydantic import BaseModel
from asgiref.sync import sync_to_async
import os
from contextlib import asynccontextmanager

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from app.models import Item

@asynccontextmanager
async def lifespan(app: FastAPI):
    await add_default_data()
    yield
    pass

app = FastAPI(lifespan=lifespan)

# Mount Django admin
django_app = get_wsgi_application()
app.mount("/django", WSGIMiddleware(django_app))

# Pydantic model for response
class ItemResponse(BaseModel):
    value: str

    class Config:
        from_attributes = True

# Function to add default data
async def add_default_data():
    create_item = sync_to_async(Item.objects.get_or_create)
    default_data = [
        {"animal": "Lion"},
        {"animal": "Tiger"},
        {"animal": "Elephant"},
    ]
    
    for data in default_data:
        await create_item(defaults=None, **data)

@app.get("/animals/", response_model=List[ItemResponse])
async def get_animals():
    get_animals = sync_to_async(lambda: list(Item.objects.values_list('animal', flat=True)))
    animals = await get_animals()
    return [{"value": animal} for animal in animals]
