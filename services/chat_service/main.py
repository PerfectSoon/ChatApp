from contextlib import asynccontextmanager

import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.models import Base
from database.connection import  engine
from settings import settings
from api.routers.rest import router
from api.routers.websocket import router1


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


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
app.include_router(router1)


app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def read_root():
    return {"message": f"{settings.service_name} is running"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="localhost", port=8002, reload=True)