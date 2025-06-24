import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database.session import get_thread_local_session_manager
from fastapi import FastAPI
from api.routers import main_api_router
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if get_thread_local_session_manager()._engine is not None:
        # Close the DB connection
        await get_thread_local_session_manager().close()

app = FastAPI(title="Spy Cat Agency", lifespan=lifespan, docs_url="/api/docs")

app.include_router(main_api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Spy Cat Agency"}


@app.get("/ping")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
