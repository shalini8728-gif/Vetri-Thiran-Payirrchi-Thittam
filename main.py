from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import router


# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent


# Application startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables when the application starts
    init_db()

    yield


# Create FastAPI application
app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    description="AI-powered personalized fitness plan generator using Google Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)


# Static files (CSS)
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


# Application routes
app.include_router(router)