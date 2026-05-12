import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine
from models import Base
from dependencies import get_current_user
from schemas import UserResponse
from routers import auth, characters, inventory, admin, shop

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DnD Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(auth.router)
app.include_router(characters.router)
app.include_router(inventory.router)
app.include_router(admin.router)
app.include_router(shop.router)


@app.get("/auth/me", response_model=UserResponse, tags=["auth"])
def me(user=Depends(get_current_user)):
    return user


@app.get("/health")
def health():
    return {"status": "ok"}
