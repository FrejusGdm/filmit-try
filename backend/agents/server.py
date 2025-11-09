from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from profile_agent import ProfileAgent
from director_workflow import DirectorWorkflow, DirectorState
from viral_formats import seed_viral_formats
from langchain_core.messages import HumanMessage
import shutil


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Chat Models
class ChatMessage(BaseModel):
    session_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    session_id: str
    message: str
    confidence_scores: Optional[Dict[str, float]] = {}
    summary_status: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = {}

class SessionCreate(BaseModel):
    user_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    created_at: str

# Director Workflow Models
class DirectorProjectCreate(BaseModel):
    user_goal: str
    product_type: Optional[str] = "general"
    target_platform: Optional[str] = "YouTube"

class DirectorMessageInput(BaseModel):
    project_id: str
    message: str

class DirectorResponse(BaseModel):
    project_id: str
    message: str
    current_step: str
    shot_list: Optional[List[Dict[str, Any]]] = None
    matched_format: Optional[Dict[str, Any]] = None
    user_input_needed: bool = False

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Chat Endpoints
@api_router.post("/chat/session", response_model=SessionResponse)
async def create_chat_session(input: SessionCreate):
    """Create a new chat session for profile building"""
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "user_id": input.user_id or "anonymous",
        "profile_data": {},
        "confidence_scores": {},
        "conversation_history": [],
        "profile_summary": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.profile_sessions.insert_one(session_data)
    
    return SessionResponse(
        session_id=session_id,
        created_at=session_data["created_at"]
    )

@api_router.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(input: ChatMessage):
    """Send a message to the ProfileAgent and get a response"""
    try:
        # Initialize ProfileAgent
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
        
        agent = ProfileAgent(db=db, api_key=api_key)
        
        # Process the message
        result = await agent.process_message(
            session_id=input.session_id,
            user_message=input.message,
            conversation_history=input.conversation_history or []
        )
        
        return ChatResponse(
            session_id=input.session_id,
            message=result["message"],
            confidence_scores=result.get("confidence_scores", {}),
            summary_status=result.get("summary_status"),
            profile_data=result.get("profile_data", {})
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/session/{session_id}")
async def get_chat_session(session_id: str):
    """Retrieve session summary for MatchingAgent"""
    session = await db.profile_sessions.find_one({"session_id": session_id}, {"_id": 0})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

# Director Workflow Endpoints
@api_router.post("/director/project", response_model=DirectorResponse)
async def create_director_project(input: DirectorProjectCreate):
    """Create a new video project with the Director workflow"""
    try:
        project_id = str(uuid.uuid4())
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if not api_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
        
        # Initialize Director workflow
        workflow = DirectorWorkflow(db=db, api_key=api_key)
        
        # Create initial state
        initial_state: DirectorState = {
            "messages": [HumanMessage(content=input.user_goal)],
            "project_id": project_id,
            "user_goal": input.user_goal,
            "product_type": input.product_type,
            "target_platform": input.target_platform,
            "matched_format": None,
            "shot_list": None,
            "uploaded_segments": [],
            "edited_video_path": None,
            "current_step": "initial",
            "user_input_needed": False,
            "next_instruction": ""
        }
        
        # Run the workflow
        result = await workflow.graph.ainvoke(initial_state)
        
        # Extract latest AI message
        ai_messages = [m for m in result["messages"] if hasattr(m, 'content')]
        latest_message = ai_messages[-1].content if ai_messages else "Project created successfully!"
        
        return DirectorResponse(
            project_id=project_id,
            message=latest_message,
            current_step=result.get("current_step", "initial"),
            shot_list=result.get("shot_list"),
            matched_format=result.get("matched_format"),
            user_input_needed=result.get("user_input_needed", False)
        )
    except Exception as e:
        logger.error(f"Error creating director project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/director/message", response_model=DirectorResponse)
async def send_director_message(input: DirectorMessageInput):
    """Send a message in an existing Director project"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if not api_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
        
        # Load project state from database
        project = await db.video_projects.find_one({"project_id": input.project_id}, {"_id": 0})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Initialize workflow
        workflow = DirectorWorkflow(db=db, api_key=api_key)
        
        # Reconstruct state from project data
        state: DirectorState = {
            "messages": project.get("messages", []) + [HumanMessage(content=input.message)],
            "project_id": input.project_id,
            "user_goal": project.get("user_goal", ""),
            "product_type": project.get("product_type", "general"),
            "target_platform": project.get("target_platform", "YouTube"),
            "matched_format": project.get("matched_format"),
            "shot_list": project.get("shot_list"),
            "uploaded_segments": project.get("uploaded_segments", []),
            "edited_video_path": project.get("edited_video_path"),
            "current_step": project.get("current_step", "initial"),
            "user_input_needed": False,
            "next_instruction": ""
        }
        
        # Run workflow
        result = await workflow.graph.ainvoke(state)
        
        # Extract latest AI message
        ai_messages = [m for m in result["messages"] if hasattr(m, 'content')]
        latest_message = ai_messages[-1].content if ai_messages else "Processing..."
        
        return DirectorResponse(
            project_id=input.project_id,
            message=latest_message,
            current_step=result.get("current_step", "initial"),
            shot_list=result.get("shot_list"),
            matched_format=result.get("matched_format"),
            user_input_needed=result.get("user_input_needed", False)
        )
    except Exception as e:
        logger.error(f"Error processing director message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/director/upload-segment")
async def upload_video_segment(
    project_id: str,
    segment_name: str,
    file: UploadFile = File(...)
):
    """Upload a video segment for a project"""
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path("/app/backend/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{project_id}_{segment_name}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update project in database
        segment_data = {
            "segment_name": segment_name,
            "file_path": str(file_path),
            "filename": file.filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.video_projects.update_one(
            {"project_id": project_id},
            {"$push": {"uploaded_segments": segment_data}}
        )
        
        return {
            "success": True,
            "message": f"Segment '{segment_name}' uploaded successfully",
            "file_path": str(file_path)
        }
    except Exception as e:
        logger.error(f"Error uploading segment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/director/project/{project_id}")
async def get_director_project(project_id: str):
    """Get project details"""
    project = await db.video_projects.find_one({"project_id": project_id}, {"_id": 0})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    """Seed viral formats on startup"""
    try:
        await seed_viral_formats(db)
        logger.info("Viral formats seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding viral formats: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()