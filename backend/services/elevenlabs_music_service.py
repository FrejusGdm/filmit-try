"""
ElevenLabs Music Generation Service
Integrates with ElevenLabs Music API for AI music composition
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from elevenlabs.client import AsyncElevenLabs
from pathlib import Path

logger = logging.getLogger(__name__)


class ElevenLabsMusicService:
    """Service for generating music with ElevenLabs Music API"""
    
    def __init__(self):
        # Get API key from environment
        api_key = os.environ.get('ELEVENLABS_API_KEY')
        if not api_key:
            logger.warning("No ElevenLabs API key found. Music generation will not work.")
            self.client = None
        else:
            self.client = AsyncElevenLabs(api_key=api_key)
        
        # Set up music uploads directory
        self.uploads_dir = Path(__file__).parent.parent / 'uploads' / 'music'
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ElevenLabs Music Service initialized. Uploads dir: {self.uploads_dir}")
    
    async def generate_music(
        self,
        prompt: str,
        music_length_ms: int,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Generate music using ElevenLabs Music API
        
        Args:
            prompt: Text description of the music to generate
            music_length_ms: Duration in milliseconds (10000-60000)
            project_id: Project ID for file naming
        
        Returns:
            Dictionary with file_path, filename, and metadata
        """
        if not self.client:
            raise ValueError("ElevenLabs Music service not initialized. Missing API key.")
        
        try:
            logger.info(f"Generating music for project {project_id}")
            logger.info(f"Prompt: {prompt[:200]}...")
            logger.info(f"Duration: {music_length_ms}ms ({music_length_ms / 1000}s)")
            
            # Call ElevenLabs Music API to compose track
            track = await self.client.music.compose(
                prompt=prompt,
                music_length_ms=music_length_ms
            )
            
            # Generate filename
            filename = f"{project_id}_music_{music_length_ms}ms.mp3"
            file_path = self.uploads_dir / filename
            
            logger.info(f"Saving generated music to: {file_path}")
            
            # Write audio content to file
            # track is an async iterator that yields bytes
            with open(file_path, 'wb') as f:
                async for chunk in track:
                    f.write(chunk)
            
            logger.info(f"Music generation completed successfully: {filename}")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": filename,
                "duration_ms": music_length_ms,
                "duration_seconds": music_length_ms / 1000,
                "project_id": project_id
            }
            
        except Exception as e:
            logger.error(f"Error generating music: {str(e)}")
            raise
    
    async def generate_music_detailed(
        self,
        prompt: str,
        music_length_ms: int,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Generate music with detailed composition plan
        
        This returns both the audio and the composition plan used
        
        Args:
            prompt: Text description of the music
            music_length_ms: Duration in milliseconds
            project_id: Project ID for file naming
        
        Returns:
            Dictionary with file_path, filename, composition_plan, and song_metadata
        """
        if not self.client:
            raise ValueError("ElevenLabs Music service not initialized. Missing API key.")
        
        try:
            logger.info(f"Generating detailed music for project {project_id}")
            
            # Get detailed response with composition plan
            track_details = await self.client.music.compose_detailed(
                prompt=prompt,
                music_length_ms=music_length_ms
            )
            
            # Generate filename
            filename = f"{project_id}_music_{music_length_ms}ms.mp3"
            file_path = self.uploads_dir / filename
            
            logger.info(f"Saving detailed music to: {file_path}")
            
            # Write audio bytes to file
            with open(file_path, 'wb') as f:
                f.write(track_details.audio)
            
            logger.info(f"Detailed music generation completed: {filename}")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": filename,
                "duration_ms": music_length_ms,
                "duration_seconds": music_length_ms / 1000,
                "project_id": project_id,
                "composition_plan": track_details.json.get("composition_plan"),
                "song_metadata": track_details.json.get("song_metadata")
            }
            
        except Exception as e:
            logger.error(f"Error generating detailed music: {str(e)}")
            raise
    
    def get_music_file_path(self, filename: str) -> Optional[Path]:
        """
        Get full path to a music file
        
        Args:
            filename: Name of the music file
        
        Returns:
            Path object if file exists, None otherwise
        """
        file_path = self.uploads_dir / filename
        
        if file_path.exists():
            return file_path
        
        return None


# Global instance
elevenlabs_music_service = ElevenLabsMusicService()
