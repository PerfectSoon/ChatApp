import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from database.models import Base
from database.connection import  engine, SessionLocal
from settings import settings
from api.rest import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db.close()


app = FastAPI(
    title=settings.service_name,
    description=settings.service_description,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/auth.html")

@app.get("/auth/success")
async def auth_success():
    return RedirectResponse(url="http://localhost:8001/static/chat.html")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)