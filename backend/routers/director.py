"""
Director Agent Router - LangGraph-based video creation workflow
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
import os
import logging
from pathlib import Path
import uuid
import shutil
from datetime import datetime, timezone

# Import Director workflow
import sys
sys.path.append(str(Path(__file__).parent.parent / "agents"))
from director_workflow import DirectorWorkflow, DirectorState
from viral_formats import seed_viral_formats
from langchain_core.messages import HumanMessage


logger = logging.getLogger(__name__)
router = APIRouter()


# Get database connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


# Pydantic models
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
    next_instruction: str = ""


@router.post("/project", response_model=DirectorResponse)
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
            user_input_needed=result.get("user_input_needed", False),
            next_instruction=result.get("next_instruction", "")
        )
    except Exception as e:
        logger.error(f"Error creating director project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=DirectorResponse)
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
        
        # Reconstruct messages from database
        stored_messages = project.get("messages", [])
        messages = []
        for msg in stored_messages:
            if msg.get("type") == "human":
                messages.append(HumanMessage(content=msg.get("content", "")))
        
        # Add new message
        messages.append(HumanMessage(content=input.message))
        
        # Reconstruct state from project data
        state: DirectorState = {
            "messages": messages,
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
            user_input_needed=result.get("user_input_needed", False),
            next_instruction=result.get("next_instruction", "")
        )
    except Exception as e:
        logger.error(f"Error processing director message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-segment")
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
            {
                "$push": {"uploaded_segments": segment_data},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        # Update shot list to mark segment as uploaded
        project = await db.video_projects.find_one({"project_id": project_id}, {"_id": 0})
        if project and project.get("shot_list"):
            shot_list = project["shot_list"]
            for shot in shot_list:
                if shot.get("segment_name") == segment_name:
                    shot["uploaded"] = True
            
            await db.video_projects.update_one(
                {"project_id": project_id},
                {"$set": {"shot_list": shot_list}}
            )
        
        return {
            "success": True,
            "message": f"Segment '{segment_name}' uploaded successfully",
            "file_path": str(file_path)
        }
    except Exception as e:
        logger.error(f"Error uploading segment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}")
async def get_director_project(project_id: str):
    """Get project details"""
    project = await db.video_projects.find_one({"project_id": project_id}, {"_id": 0})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.post("/seed-formats")
async def seed_formats():
    """Seed viral formats database (admin endpoint)"""
    try:
        await seed_viral_formats(db)
        return {"success": True, "message": "Viral formats seeded successfully"}
    except Exception as e:
        logger.error(f"Error seeding formats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Video Assembly Endpoints
from services.video_assembly_service import VideoAssemblyService

# Create assembly service instance
assembly_service = VideoAssemblyService(db)


class AssemblyOptions(BaseModel):
    add_transitions: bool = True
    transition_type: str = Field(default="fade", description="fade, wipe, dissolve, slidedown, slideup")
    transition_duration: float = 0.8
    add_subtitles: bool = True
    subtitle_position: str = Field(default="bottom", description="top, center, bottom")
    subtitle_font_size: int = 48
    optimize_platform: Optional[str] = Field(default="youtube", description="tiktok, instagram, youtube")


class AssembleVideoRequest(BaseModel):
    project_id: str
    options: Optional[AssemblyOptions] = None


@router.post("/assemble")
async def assemble_project_video(request: AssembleVideoRequest):
    """
    Assemble all project segments into final video with transitions and effects
    
    This endpoint:
    1. Collects all uploaded segments for the project
    2. Adds subtitles from shot scripts (if enabled)
    3. Merges segments with transitions
    4. Optimizes for target platform
    """
    try:
        project_id = request.project_id
        
        # Get project details
        project = await db.video_projects.find_one({"project_id": project_id}, {"_id": 0})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get shot list
        shot_list = project.get("shot_list", [])
        if not shot_list:
            raise HTTPException(status_code=400, detail="Project has no shot list")
        
        # Get uploaded segments
        segment_paths = await assembly_service.get_project_segments(project_id)
        
        if not segment_paths:
            raise HTTPException(
                status_code=400, 
                detail="No video segments found. Please upload segments first."
            )
        
        logger.info(f"Starting assembly for project {project_id} with {len(segment_paths)} segments")
        
        # Convert options to dict
        options_dict = request.options.model_dump() if request.options else {}
        
        # Start assembly
        assembly_id = await assembly_service.start_assembly(
            project_id=project_id,
            segment_paths=segment_paths,
            shot_list=shot_list,
            options=options_dict
        )
        
        return {
            "success": True,
            "assembly_id": assembly_id,
            "message": f"Video assembly started. Processing {len(segment_paths)} segments.",
            "segments_count": len(segment_paths)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting video assembly: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Shot Management Endpoints

class ShotUpdate(BaseModel):
    project_id: str
    shot_index: int
    segment_name: Optional[str] = None
    script: Optional[str] = None
    visual_guide: Optional[str] = None
    duration: Optional[int] = None


class ShotAdd(BaseModel):
    project_id: str
    segment_name: str
    script: str
    visual_guide: str
    duration: int = 15


class ShotDelete(BaseModel):
    project_id: str
    shot_index: int


class ShotReorder(BaseModel):
    project_id: str
    shot_list: List[Dict[str, Any]]


@router.put("/shot/update")
async def update_shot(input: ShotUpdate):
    """Update an existing shot in the shot list"""
    try:
        project = await db.video_projects.find_one({"project_id": input.project_id}, {"_id": 0})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get shot list
        shot_list = project.get("shot_list", [])
        
        if input.shot_index < 0 or input.shot_index >= len(shot_list):
            raise HTTPException(status_code=400, detail="Invalid shot index")
        
        # Update shot fields
        shot = shot_list[input.shot_index]
        if input.segment_name is not None:
            shot["segment_name"] = input.segment_name
        if input.script is not None:
            shot["script"] = input.script
        if input.visual_guide is not None:
            shot["visual_guide"] = input.visual_guide
        if input.duration is not None:
            shot["duration"] = input.duration
        
        # Save to database
        await db.video_projects.update_one(
            {"project_id": input.project_id},
            {
                "$set": {
                    "shot_list": shot_list,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "shot_list": shot_list,
            "message": "Shot updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating shot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assembly-status/{assembly_id}")
async def get_assembly_status(assembly_id: str):
    """
    Get status of video assembly job
    
    Returns progress, status, and output path when complete
    """
    try:
        status = await assembly_service.get_assembly_status(assembly_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Assembly job not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assembly status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{assembly_id}")
async def download_assembled_video(assembly_id: str):
    """
    Download the assembled video file
    """
    from fastapi.responses import FileResponse
    
    try:
        status = await assembly_service.get_assembly_status(assembly_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Assembly job not found")
        
        if status['status'] != 'completed':
            raise HTTPException(
                status_code=400, 
                detail=f"Assembly not complete. Status: {status['status']}"
            )
        
        output_path = status['output_path']
        
        if not output_path or not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        # Get filename from path
        filename = Path(output_path).name
        
        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename=f"assembled_{filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shot/add")
async def add_shot(input: ShotAdd):
    """Add a new shot to the shot list"""
    try:
        project = await db.video_projects.find_one({"project_id": input.project_id}, {"_id": 0})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        shot_list = project.get("shot_list", [])
        
        # Create new shot
        new_shot = {
            "segment_name": input.segment_name,
            "script": input.script,
            "visual_guide": input.visual_guide,
            "duration": input.duration,
            "uploaded": False,
            "required": False  # All shots are now optional
        }
        
        shot_list.append(new_shot)
        
        # Save to database
        await db.video_projects.update_one(
            {"project_id": input.project_id},
            {
                "$set": {
                    "shot_list": shot_list,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Shot added successfully",
            "shot_list": shot_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding shot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/shot/delete")
async def delete_shot(input: ShotDelete):
    """Delete a shot from the shot list"""
    try:
        project = await db.video_projects.find_one({"project_id": input.project_id}, {"_id": 0})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        shot_list = project.get("shot_list", [])
        
        if input.shot_index < 0 or input.shot_index >= len(shot_list):
            raise HTTPException(status_code=400, detail="Invalid shot index")
        
        # Remove shot
        deleted_shot = shot_list.pop(input.shot_index)
        
        # Save to database
        await db.video_projects.update_one(
            {"project_id": input.project_id},
            {
                "$set": {
                    "shot_list": shot_list,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": f"Shot '{deleted_shot.get('segment_name')}' deleted successfully",
            "shot_list": shot_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting shot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/shot/reorder")
async def reorder_shots(input: ShotReorder):
    """Reorder the shot list"""
    try:
        project = await db.video_projects.find_one({"project_id": input.project_id}, {"_id": 0})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Save reordered shot list to database
        await db.video_projects.update_one(
            {"project_id": input.project_id},
            {
                "$set": {
                    "shot_list": input.shot_list,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Shot list reordered successfully",
            "shot_list": input.shot_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering shots: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# ==================== Sora 2 Video Generation ====================

from services.sora_service import sora_service
from fastapi import BackgroundTasks


class SoraGenerateRequest(BaseModel):
    """Request model for Sora video generation"""
    project_id: str
    shot_index: int
    model: str = Field(default="sora-2", description="sora-2 or sora-2-pro")
    size: str = Field(default="1280x720", description="Video resolution")


class SoraStatusResponse(BaseModel):
    """Response model for Sora generation status"""
    video_id: str
    status: str  # queued, in_progress, completed, failed
    progress: int  # 0-100
    file_path: Optional[str] = None
    error: Optional[str] = None


@router.post("/generate-shot")
async def generate_shot_with_sora(
    input: SoraGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a video shot using Sora 2 API
    
    This initiates an async video generation job. Use the returned job_id
    to check status with the /sora-status/{job_id} endpoint.
    """
    try:
        # Get project and shot details
        project = await db.video_projects.find_one(
            {"project_id": input.project_id},
            {"_id": 0}
        )
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        shot_list = project.get("shot_list", [])
        
        if input.shot_index < 0 or input.shot_index >= len(shot_list):
            raise HTTPException(status_code=400, detail="Invalid shot index")
        
        shot = shot_list[input.shot_index]
        
        # Validate model choice
        if input.model not in ["sora-2", "sora-2-pro"]:
            raise HTTPException(
                status_code=400,
                detail="Model must be 'sora-2' or 'sora-2-pro'"
            )
        
        logger.info(f"Starting Sora generation for project {input.project_id}, shot: {shot['segment_name']}")
        
        # Start video generation (non-blocking)
        result = await sora_service.generate_video(
            prompt=shot.get("script", ""),
            visual_description=shot.get("visual_guide", ""),
            duration=shot.get("duration", 5),
            segment_name=shot.get("segment_name", "shot"),
            project_id=input.project_id,
            size=input.size,
            model=input.model
        )
        
        # Store job info in database for tracking
        job_id = result["video_id"]
        await db.sora_jobs.insert_one({
            "job_id": job_id,
            "project_id": input.project_id,
            "shot_index": input.shot_index,
            "segment_name": shot["segment_name"],
            "status": result["status"],
            "progress": result.get("progress", 0),
            "model": input.model,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "video_id": result["video_id"]
        })
        
        return {
            "success": True,
            "job_id": job_id,
            "status": result["status"],
            "progress": result.get("progress", 0),
            "message": f"Video generation started for {shot['segment_name']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting Sora generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sora-status/{job_id}")
async def check_sora_status(job_id: str):
    """
    Check the status of a Sora video generation job
    
    Returns current status, progress (0-100), and file path when completed.
    """
    try:
        # Get job from database
        job = await db.sora_jobs.find_one({"job_id": job_id}, {"_id": 0})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check current status from Sora API
        status_result = await sora_service.check_video_status(job_id)
        
        # Update database with latest status
        await db.sora_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": status_result["status"],
                    "progress": status_result.get("progress", 0),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        response = {
            "job_id": job_id,
            "status": status_result["status"],
            "progress": status_result.get("progress", 0),
            "project_id": job["project_id"],
            "segment_name": job["segment_name"]
        }
        
        # If completed, download the video
        if status_result["status"] == "completed" and not job.get("file_path"):
            try:
                file_path = await sora_service.download_completed_video(
                    video_id=job_id,
                    project_id=job["project_id"],
                    segment_name=job["segment_name"]
                )
                
                # Update database with file path
                await db.sora_jobs.update_one(
                    {"job_id": job_id},
                    {"$set": {"file_path": file_path}}
                )
                
                # Update shot list to mark as uploaded
                project = await db.video_projects.find_one(
                    {"project_id": job["project_id"]},
                    {"_id": 0}
                )
                
                if project:
                    shot_list = project.get("shot_list", [])
                    shot_index = job["shot_index"]
                    
                    if 0 <= shot_index < len(shot_list):
                        shot_list[shot_index]["uploaded"] = True
                        shot_list[shot_index]["file_path"] = file_path
                        shot_list[shot_index]["generated_by_sora"] = True
                        
                        await db.video_projects.update_one(
                            {"project_id": job["project_id"]},
                            {"$set": {"shot_list": shot_list}}
                        )
                
                response["file_path"] = file_path
                response["success"] = True
                
            except Exception as e:
                logger.error(f"Error downloading completed video: {str(e)}")
                response["error"] = str(e)
        
        elif status_result["status"] == "failed":
            error_msg = status_result.get("error", "Unknown error")
            response["error"] = error_msg
            response["success"] = False
            
            # Update database with error
            await db.sora_jobs.update_one(
                {"job_id": job_id},
                {"$set": {"error": error_msg}}
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking Sora status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sora-job/{job_id}")
async def cancel_sora_job(job_id: str):
    """
    Cancel/delete a Sora generation job
    
    Note: Sora API doesn't support cancellation once started,
    but we can remove it from our tracking.
    """
    try:
        result = await db.sora_jobs.delete_one({"job_id": job_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "message": "Job removed from tracking"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Sora job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/video-preview/{project_id}/{filename}")
async def serve_video_preview(project_id: str, filename: str):
    """
    Serve generated video files for preview
    
    This endpoint serves video files from the uploads directory
    for preview in the frontend.
    """
    try:
        # Construct file path
        uploads_dir = Path(__file__).parent.parent / 'uploads'
        file_path = uploads_dir / filename
        
        # Security check: ensure file is in uploads directory
        if not file_path.is_relative_to(uploads_dir):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Return video file
        return FileResponse(
            path=str(file_path),
            media_type="video/mp4",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving video preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
