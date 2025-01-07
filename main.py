import django
from django.conf import settings
from fastapi import FastAPI
from django.core.asgi import get_asgi_application
from typing import List
from pydantic import BaseModel
from asgiref.sync import sync_to_async
import os
from sse_starlette.sse import EventSourceResponse
from contextlib import asynccontextmanager
import asyncio
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

# Mount Django as ASGI
django_asgi_app = get_asgi_application()
app.mount("/django", django_asgi_app)

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

# WebSocket example
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")

async def event_generator():
    while True:
        yield {
            "event": "update",
            "data": "Server Time Update"
        }
        await asyncio.sleep(1)

@app.get("/events")
async def events():
    return EventSourceResponse(event_generator())