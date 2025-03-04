from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    description=settings.service_description
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Auth service is running"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)