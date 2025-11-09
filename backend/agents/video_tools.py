"""
Video editing tools using FFMPEG for the Director system.
Provides MCP-style tools for video manipulation operations.
"""

import ffmpeg
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


# File storage paths
UPLOAD_DIR = Path("/app/backend/uploads")
PROCESSED_DIR = Path("/app/backend/processed")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# ffmpeg binary paths
FFMPEG_BIN = "/usr/bin/ffmpeg"
FFPROBE_BIN = "/usr/bin/ffprobe"


async def ffmpeg_merge_videos(
    input_files: List[str],
    output_file: str,
    transition_duration: float = 0.5
) -> Dict[str, Any]:
    """
    Concatenate multiple video segments with optional transitions.
    
    Args:
        input_files: List of input video file paths
        output_file: Output video file path
        transition_duration: Duration of transition effect in seconds
    
    Returns:
        Success status and output file path
    """
    try:
        # Create concat file list
        concat_list_path = PROCESSED_DIR / f"concat_{datetime.now().timestamp()}.txt"
        with open(concat_list_path, 'w') as f:
            for video_file in input_files:
                f.write(f"file '{video_file}'\n")
        
        output_path = PROCESSED_DIR / output_file
        
        # Use ffmpeg concat demuxer for fast concatenation
        command = [
            FFMPEG_BIN, '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_list_path),
            '-c', 'copy',
            str(output_path)
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        # Clean up concat list
        concat_list_path.unlink()
        
        return {
            "success": True,
            "output_file": str(output_path),
            "message": f"Merged {len(input_files)} videos successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to merge videos"
        }


async def ffmpeg_cut_video(
    input_file: str,
    output_file: str,
    start_time: str,
    end_time: Optional[str] = None,
    duration: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cut/trim video by timestamps or duration.
    
    Args:
        input_file: Input video file path
        output_file: Output video file path
        start_time: Start timestamp (format: HH:MM:SS or seconds)
        end_time: End timestamp (optional if duration provided)
        duration: Duration to cut (optional if end_time provided)
    
    Returns:
        Success status and output file path
    """
    try:
        input_path = Path(input_file)
        output_path = PROCESSED_DIR / output_file
        
        command = [FFMPEG_BIN, '-y', '-i', str(input_path), '-ss', start_time]
        
        if end_time:
            command.extend(['-to', end_time])
        elif duration:
            command.extend(['-t', duration])
        
        command.extend(['-c', 'copy', str(output_path)])
        
        subprocess.run(command, check=True, capture_output=True)
        
        return {
            "success": True,
            "output_file": str(output_path),
            "message": f"Cut video from {start_time} successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to cut video"
        }


async def ffmpeg_add_subtitles(
    input_file: str,
    output_file: str,
    subtitle_text: str,
    font_size: int = 24,
    font_color: str = "white",
    background_color: str = "black@0.5",
    position: str = "bottom"
) -> Dict[str, Any]:
    """
    Add subtitles/text overlay to video.
    
    Args:
        input_file: Input video file path
        output_file: Output video file path
        subtitle_text: Text to display
        font_size: Font size
        font_color: Font color
        background_color: Background color with transparency
        position: Position (top, center, bottom)
    
    Returns:
        Success status and output file path
    """
    try:
        input_path = Path(input_file)
        output_path = PROCESSED_DIR / output_file
        
        # Position mapping
        positions = {
            "top": "x=(w-text_w)/2:y=50",
            "center": "x=(w-text_w)/2:y=(h-text_h)/2",
            "bottom": "x=(w-text_w)/2:y=h-text_h-50"
        }
        
        pos_str = positions.get(position, positions["bottom"])
        
        # Build drawtext filter
        drawtext = (
            f"drawtext=text='{subtitle_text}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"box=1:boxcolor={background_color}:"
            f"{pos_str}"
        )
        
        command = [
            FFMPEG_BIN, '-y',
            '-i', str(input_path),
            '-vf', drawtext,
            '-codec:a', 'copy',
            str(output_path)
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        return {
            "success": True,
            "output_file": str(output_path),
            "message": "Added subtitles successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add subtitles"
        }


async def ffmpeg_add_transition(
    video1: str,
    video2: str,
    output_file: str,
    transition_type: str = "fade",
    duration: float = 1.0
) -> Dict[str, Any]:
    """
    Add transition effect between two videos.
    
    Args:
        video1: First video file path
        video2: Second video file path
        output_file: Output video file path
        transition_type: Type of transition (fade, wipe, dissolve)
        duration: Transition duration in seconds
    
    Returns:
        Success status and output file path
    """
    try:
        output_path = PROCESSED_DIR / output_file
        
        # For fade transition (xfade filter)
        command = [
            FFMPEG_BIN, '-y',
            '-i', video1,
            '-i', video2,
            '-filter_complex',
            f'[0][1]xfade=transition={transition_type}:duration={duration}:offset=0[out]',
            '-map', '[out]',
            str(output_path)
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        return {
            "success": True,
            "output_file": str(output_path),
            "message": f"Added {transition_type} transition successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add transition"
        }


async def ffmpeg_resize_video(
    input_file: str,
    output_file: str,
    width: int,
    height: int,
    maintain_aspect: bool = True
) -> Dict[str, Any]:
    """
    Resize video to specified dimensions.
    
    Args:
        input_file: Input video file path
        output_file: Output video file path
        width: Target width
        height: Target height
        maintain_aspect: Maintain aspect ratio
    
    Returns:
        Success status and output file path
    """
    try:
        input_path = Path(input_file)
        output_path = PROCESSED_DIR / output_file
        
        if maintain_aspect:
            scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        else:
            scale_filter = f"scale={width}:{height}"
        
        command = [
            FFMPEG_BIN, '-y',
            '-i', str(input_path),
            '-vf', scale_filter,
            '-c:a', 'copy',
            str(output_path)
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        return {
            "success": True,
            "output_file": str(output_path),
            "message": f"Resized video to {width}x{height}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to resize video"
        }


async def ffmpeg_adjust_audio(
    input_file: str,
    output_file: str,
    volume: float = 1.0,
    normalize: bool = False
) -> Dict[str, Any]:
    """
    Adjust audio volume or normalize audio levels.
    
    Args:
        input_file: Input video file path
        output_file: Output video file path
        volume: Volume multiplier (1.0 = original, 0.5 = half, 2.0 = double)
        normalize: Apply audio normalization
    
    Returns:
        Success status and output file path
    """
    try:
        input_path = Path(input_file)
        output_path = PROCESSED_DIR / output_file
        
        if normalize:
            audio_filter = "loudnorm"
        else:
            audio_filter = f"volume={volume}"
        
        command = [
            FFMPEG_BIN, '-y',
            '-i', str(input_path),
            '-af', audio_filter,
            '-c:v', 'copy',
            str(output_path)
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        return {
            "success": True,
            "output_file": str(output_path),
            "message": "Adjusted audio successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to adjust audio"
        }


async def get_video_metadata(input_file: str) -> Dict[str, Any]:
    """
    Extract video metadata (duration, resolution, codec, etc.).
    
    Args:
        input_file: Input video file path
    
    Returns:
        Video metadata dictionary
    """
    try:
        command = [
            FFPROBE_BIN,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            input_file
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout)
        
        # Extract relevant info
        video_stream = next((s for s in metadata['streams'] if s['codec_type'] == 'video'), None)
        audio_stream = next((s for s in metadata['streams'] if s['codec_type'] == 'audio'), None)
        
        return {
            "success": True,
            "duration": float(metadata['format'].get('duration', 0)),
            "size_bytes": int(metadata['format'].get('size', 0)),
            "format": metadata['format'].get('format_name', 'unknown'),
            "video": {
                "codec": video_stream.get('codec_name') if video_stream else None,
                "width": video_stream.get('width') if video_stream else None,
                "height": video_stream.get('height') if video_stream else None,
                "fps": eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else None
            },
            "audio": {
                "codec": audio_stream.get('codec_name') if audio_stream else None,
                "sample_rate": audio_stream.get('sample_rate') if audio_stream else None,
                "channels": audio_stream.get('channels') if audio_stream else None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get video metadata"
        }


async def optimize_for_platform(
    input_file: str,
    output_file: str,
    platform: str
) -> Dict[str, Any]:
    """
    Optimize video for specific platforms (TikTok, Instagram, YouTube).
    
    Args:
        input_file: Input video file path
        output_file: Output video file path
        platform: Target platform (tiktok, instagram, youtube)
    
    Returns:
        Success status and output file path
    """
    try:
        input_path = Path(input_file)
        output_path = PROCESSED_DIR / output_file
        
        # Platform-specific settings
        platform_specs = {
            "tiktok": {
                "size": "1080:1920",  # 9:16 aspect ratio
                "bitrate": "4000k",
                "max_duration": 180
            },
            "instagram": {
                "size": "1080:1920",  # 9:16 for reels
                "bitrate": "3500k",
                "max_duration": 90
            },
            "youtube": {
                "size": "1920:1080",  # 16:9 aspect ratio
                "bitrate": "8000k",
                "max_duration": None
            }
        }
        
        specs = platform_specs.get(platform.lower(), platform_specs["youtube"])
        
        command = [
            FFMPEG_BIN, '-y',
            '-i', str(input_path),
            '-vf', f"scale={specs['size']}:force_original_aspect_ratio=decrease,pad={specs['size'].replace(':', 'x')}:(ow-iw)/2:(oh-ih)/2",
            '-b:v', specs['bitrate'],
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            str(output_path)
        ]
        
        subprocess.run(command, check=True, capture_output=True)
        
        return {
            "success": True,
            "output_file": str(output_path),
            "platform": platform,
            "message": f"Optimized for {platform}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to optimize for {platform}"
        }