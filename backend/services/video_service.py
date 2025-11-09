import os
import logging
import base64
import aiofiles
from pathlib import Path
from typing import Optional, Dict
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoUploadService:
    """Service for handling chunked video uploads."""
    
    def __init__(self, upload_dir: str = "/app/backend/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = self.upload_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.active_uploads = {}  # Track ongoing uploads
    
    async def handle_chunk(
        self,
        session_id: str,
        filename: str,
        chunk_index: int,
        total_chunks: int,
        chunk_data: str
    ) -> Dict:
        """Handle a single chunk of file upload."""
        try:
            # Decode base64 chunk
            chunk_bytes = base64.b64decode(chunk_data)
            
            # Create temp file path
            upload_key = f"{session_id}_{filename}"
            temp_file = self.temp_dir / f"{upload_key}.part"
            
            # Track upload progress
            if upload_key not in self.active_uploads:
                self.active_uploads[upload_key] = {
                    "received_chunks": set(),
                    "total_chunks": total_chunks,
                    "filename": filename,
                    "session_id": session_id
                }
            
            # Append chunk to temp file
            async with aiofiles.open(temp_file, "ab") as f:
                await f.write(chunk_bytes)
            
            self.active_uploads[upload_key]["received_chunks"].add(chunk_index)
            
            # Check if all chunks received
            if len(self.active_uploads[upload_key]["received_chunks"]) == total_chunks:
                final_path = await self._finalize_upload(upload_key, filename)
                return {
                    "status": "completed",
                    "file_path": str(final_path),
                    "message": "Upload completed successfully"
                }
            
            return {
                "status": "in_progress",
                "chunks_received": len(self.active_uploads[upload_key]["received_chunks"]),
                "total_chunks": total_chunks,
                "message": f"Chunk {chunk_index + 1}/{total_chunks} received"
            }
            
        except Exception as e:
            logger.error(f"Error handling chunk: {str(e)}")
            raise
    
    async def _finalize_upload(self, upload_key: str, filename: str) -> Path:
        """Move temp file to final location."""
        temp_file = self.temp_dir / f"{upload_key}.part"
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        ext = Path(filename).suffix
        final_filename = f"{file_id}{ext}"
        final_path = self.upload_dir / final_filename
        
        # Move file
        temp_file.rename(final_path)
        
        # Cleanup tracking
        del self.active_uploads[upload_key]
        
        logger.info(f"Upload finalized: {final_path}")
        return final_path
    
    async def get_video_info(self, file_path: str) -> Dict:
        """Get video file information."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Video file not found: {file_path}")
            
            stat = path.stat()
            return {
                "file_path": str(path),
                "file_size": stat.st_size,
                "filename": path.name,
                "exists": True
            }
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise
    
    async def delete_video(self, file_path: str) -> bool:
        """Delete a video file."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted video: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting video: {str(e)}")
            return False

# Global instance
video_service = VideoUploadService()