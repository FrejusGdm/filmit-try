from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager

# Import routers
from routers import videos, suggestions, chat, trends, director, research, auth
from services.tiktok_service import tiktok_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting filmit! backend server...")
    logger.info("Initializing TikTok trends service...")
    await tiktok_service.initialize()
    
    # Seed viral formats for Director
    logger.info("Seeding viral video formats...")
    import sys
    sys.path.append(str(Path(__file__).parent / "agents"))
    from viral_formats import seed_viral_formats
    await seed_viral_formats(db)
    
    logger.info("Services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down filmit! backend server...")
    await tiktok_service.close()
    client.close()
    logger.info("Shutdown complete")

# Create the main app with lifespan
app = FastAPI(
    title="filmit! API",
    description="You film it, we'll handle the rest - AI-powered video editing platform",
    version="1.0.0",
    lifespan=lifespan
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Health check routes
@api_router.get("/")
async def root():
    return {
        "message": "filmit! API - You film it, we'll handle the rest",
        "status": "operational",
        "version": "1.0.0"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "database": "connected",
            "tiktok_service": "initialized",
            "ai_service": "ready",
            "director_service": "operational"
        }
    }

# Legacy status endpoints
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include feature routers
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["Suggestions"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(trends.router, prefix="/trends", tags=["Trends"])
api_router.include_router(director.router, prefix="/director", tags=["Director"])
api_router.include_router(research.router, prefix="/research", tags=["Research"])

# Include the main API router in the app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)