"""
Sora 2 Video Generation Service
Integrates with OpenAI's Sora API for AI video generation
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from pathlib import Path

logger = logging.getLogger(__name__)

class SoraService:
    """Service for generating videos with Sora 2 API"""
    
    def __init__(self):
        # Use OpenAI API key (Sora uses same key)
        api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            logger.warning("No OpenAI API key found. Sora generation will not work.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        
        self.uploads_dir = Path(__file__).parent.parent / 'uploads'
        self.uploads_dir.mkdir(exist_ok=True)
    
    async def generate_video(
        self,
        prompt: str,
        visual_description: str,
        duration: int,
        segment_name: str,
        project_id: str,
        size: str = "1280x720",
        model: str = "sora-2",
        input_reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a video using Sora 2 API
        
        Args:
            prompt: Text description/script for the video
            visual_description: Visual guide for how to film it
            duration: Target duration in seconds (Sora supports up to 20s)
            segment_name: Name of the shot segment
            project_id: Project ID for file naming
            size: Video resolution (e.g., "1280x720", "1920x1080")
            model: "sora-2" (fast) or "sora-2-pro" (high quality)
            input_reference: Optional path to reference image
        
        Returns:
            Dictionary with video_id, status, and file path when completed
        """
        if not self.client:
            raise ValueError("Sora service not initialized. Missing API key.")
        
        try:
            # Combine prompt and visual description for best results
            full_prompt = self._create_full_prompt(prompt, visual_description)
            
            # Cap duration at Sora's max (20 seconds)
            duration = min(duration, 20)
            
            logger.info(f"Creating Sora video generation job: {segment_name}")
            logger.info(f"Model: {model}, Size: {size}, Duration: {duration}s")
            logger.info(f"Prompt: {full_prompt[:200]}...")
            
            # Create video generation job
            create_params = {
                "model": model,
                "prompt": full_prompt,
                "size": size,
                "seconds": str(duration)
            }
            
            # Add input reference if provided
            if input_reference and os.path.exists(input_reference):
                with open(input_reference, 'rb') as img_file:
                    create_params["input_reference"] = img_file
            
            video = await self.client.videos.create(**create_params)
            
            logger.info(f"Video generation started. ID: {video.id}, Status: {video.status}")
            
            return {
                "video_id": video.id,
                "status": video.status,
                "progress": getattr(video, "progress", 0),
                "model": model,
                "created_at": video.created_at,
                "segment_name": segment_name,
                "project_id": project_id
            }
            
        except Exception as e:
            logger.error(f"Error creating Sora video generation: {str(e)}")
            raise
    
    async def check_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job
        
        Args:
            video_id: The video generation job ID
        
        Returns:
            Dictionary with current status and progress
        """
        if not self.client:
            raise ValueError("Sora service not initialized. Missing API key.")
        
        try:
            video = await self.client.videos.retrieve(video_id)
            
            return {
                "video_id": video.id,
                "status": video.status,
                "progress": getattr(video, "progress", 0),
                "model": video.model,
                "created_at": video.created_at,
                "error": getattr(video, "error", None)
            }
            
        except Exception as e:
            logger.error(f"Error checking video status: {str(e)}")
            raise
    
    async def download_completed_video(
        self,
        video_id: str,
        project_id: str,
        segment_name: str
    ) -> str:
        """
        Download a completed video and save to uploads directory
        
        Args:
            video_id: The video generation job ID
            project_id: Project ID for file naming
            segment_name: Segment name for file naming
        
        Returns:
            Path to the saved video file
        """
        if not self.client:
            raise ValueError("Sora service not initialized. Missing API key.")
        
        try:
            # Check if video is completed
            video = await self.client.videos.retrieve(video_id)
            
            if video.status != "completed":
                raise ValueError(f"Video not completed yet. Status: {video.status}")
            
            logger.info(f"Downloading completed video: {video_id}")
            
            # Download video content
            content = await self.client.videos.download_content(video_id, variant="video")
            
            # Create filename
            filename = f"{project_id}_{segment_name}_sora_{video_id[:8]}.mp4"
            file_path = self.uploads_dir / filename
            
            # Save to file
            content.write_to_file(str(file_path))
            
            logger.info(f"Video saved to: {file_path}")
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
    
    async def generate_and_wait(
        self,
        prompt: str,
        visual_description: str,
        duration: int,
        segment_name: str,
        project_id: str,
        size: str = "1280x720",
        model: str = "sora-2",
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Generate video and wait for completion (blocks until done)
        
        Args:
            Same as generate_video, plus:
            poll_interval: Seconds between status checks
        
        Returns:
            Dictionary with video info and file path
        """
        # Start generation
        result = await self.generate_video(
            prompt=prompt,
            visual_description=visual_description,
            duration=duration,
            segment_name=segment_name,
            project_id=project_id,
            size=size,
            model=model
        )
        
        video_id = result["video_id"]
        
        # Poll until completed
        while True:
            status_result = await self.check_video_status(video_id)
            
            logger.info(f"Video {video_id} status: {status_result['status']} ({status_result['progress']}%)")
            
            if status_result["status"] == "completed":
                # Download the video
                file_path = await self.download_completed_video(
                    video_id=video_id,
                    project_id=project_id,
                    segment_name=segment_name
                )
                
                return {
                    **status_result,
                    "file_path": file_path,
                    "success": True
                }
            
            elif status_result["status"] == "failed":
                error_msg = status_result.get("error", "Unknown error")
                logger.error(f"Video generation failed: {error_msg}")
                return {
                    **status_result,
                    "success": False,
                    "error": error_msg
                }
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
    
    def _create_full_prompt(self, script: str, visual_guide: str) -> str:
        """
        Combine script and visual guide into optimized Sora prompt
        
        Sora works best with: shot type, subject, action, setting, lighting
        """
        # Clean up inputs
        script = script.strip()
        visual_guide = visual_guide.strip()
        
        # Combine for comprehensive prompt
        if visual_guide:
            full_prompt = f"{visual_guide}. {script}"
        else:
            full_prompt = script
        
        return full_prompt

# Global instance
sora_service = SoraService()
