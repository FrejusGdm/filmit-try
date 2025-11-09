# FFmpeg Setup and Configuration

## Overview

This application uses FFmpeg for video processing, including:
- Merging video segments
- Adding transitions between clips
- Adding subtitles to videos
- Optimizing videos for different platforms (YouTube, TikTok, Instagram)
- Video metadata extraction

## Dependencies

### System-Level Dependency
- **FFmpeg**: Binary executable for video processing
- **Location**: `/usr/bin/ffmpeg`
- **Version**: 5.1.7 (as of current installation)
- **Installation**: Via apt package manager

### Python Dependency
- **ffmpeg-python**: Python wrapper for FFmpeg
- **Version**: 0.2.0
- **Location**: Listed in `/app/backend/requirements.txt` (line 26)
- **Installation**: Via pip

## Installation

### Automatic Installation

Run the verification script to check and install if needed:
```bash
/app/verify_ffmpeg.sh
```

Or use the system dependencies installer:
```bash
/app/scripts/install_system_dependencies.sh
```

### Manual Installation

**Install FFmpeg binary:**
```bash
apt-get update
apt-get install -y ffmpeg
```

**Install Python wrapper:**
```bash
pip install ffmpeg-python==0.2.0
```

**Verify installation:**
```bash
ffmpeg -version
ffprobe -version
python3 -c "import ffmpeg; print('OK')"
```

## Requirements.txt Entry

The Python wrapper is already included in requirements.txt:
```
ffmpeg-python==0.2.0
```

**Location**: `/app/backend/requirements.txt` line 26

## Usage in Application

### Video Tools Module
Located at: `/app/backend/agents/video_tools.py`

**Available Functions:**
- `ffmpeg_merge_videos()` - Concatenate multiple video files
- `ffmpeg_add_transition()` - Add transition effects between videos
- `ffmpeg_add_subtitles()` - Overlay text subtitles on video
- `get_video_metadata()` - Extract video information (duration, resolution, etc.)
- `optimize_for_platform()` - Resize and format for specific platforms

### Video Assembly Service
Located at: `/app/backend/services/video_assembly_service.py`

Uses video_tools to:
1. Add subtitles to each shot segment
2. Merge segments with transitions
3. Optimize for target platform (YouTube, TikTok, Instagram)

## Supported Features

### Transition Types
- **fade**: Smooth fade between clips
- **wipe**: Directional wipe effect
- **dissolve**: Cross-dissolve transition
- **slidedown**: Slide down reveal
- **slideup**: Slide up reveal

### Platform Optimizations
- **YouTube**: 1920x1080, 16:9 aspect ratio
- **TikTok**: 1080x1920, 9:16 vertical
- **Instagram Reels**: 1080x1920, 9:16 vertical

### Subtitle Options
- Position: top, center, bottom
- Font size: 24-72px
- Auto-generated from shot scripts

## File Locations

### Uploads Directory
- **Path**: `/app/backend/uploads/`
- **Purpose**: Store user-uploaded video segments
- **Format**: `{project_id}_{segment_name}_{filename}`

### Processed Directory
- **Path**: `/app/backend/processed/`
- **Purpose**: Store assembled/processed videos
- **Format**: `{assembly_id}_final.mp4`

### Temporary Files
- Subtitle segments: `{assembly_id}_subtitle_{index}.mp4`
- Transition files: `{assembly_id}_transition_{index}.mp4`
- Merged file: `{assembly_id}_merged.mp4`

## Troubleshooting

### FFmpeg Not Found
```bash
# Check if installed
which ffmpeg

# If not found, install
apt-get update && apt-get install -y ffmpeg
```

### Python Module Import Error
```bash
# Check if module is installed
pip show ffmpeg-python

# If not found, install
pip install ffmpeg-python==0.2.0
```

### Permission Issues
```bash
# Ensure upload/processed directories exist and are writable
mkdir -p /app/backend/uploads
mkdir -p /app/backend/processed
chmod 755 /app/backend/uploads
chmod 755 /app/backend/processed
```

### Video Processing Fails
```bash
# Check FFmpeg can process videos
ffmpeg -i input.mp4 -c copy output.mp4

# Check logs
tail -f /var/log/supervisor/backend.err.log
```

## Testing FFmpeg

### Quick Test
```bash
# Create a test video (3 seconds, black screen)
ffmpeg -f lavfi -i color=c=black:s=1920x1080:d=3 test.mp4

# Verify it was created
ls -lh test.mp4
ffprobe test.mp4
```

### Full Integration Test
```bash
cd /app/backend
python3 << 'EOF'
import sys
sys.path.append('agents')
from video_tools import get_video_metadata

# Test with a real video file
metadata = get_video_metadata('/path/to/video.mp4')
print(f"Duration: {metadata.get('duration')}s")
print(f"Resolution: {metadata.get('width')}x{metadata.get('height')}")
EOF
```

## Performance Considerations

### Resource Usage
- FFmpeg is CPU-intensive for video encoding
- Transitions require re-encoding, slower than simple concatenation
- Platform optimization re-encodes video to match target specs

### Optimization Tips
- Use hardware acceleration if available (currently using software encoding)
- Limit transition duration to reduce processing time
- Avoid unnecessary re-encoding (use `-c copy` when possible)

## Security Notes

- FFmpeg processes user-uploaded videos
- Input validation is performed on file types
- File size limits should be enforced
- Processed videos are stored with unique IDs to prevent overwrites

## Maintenance

### Updating FFmpeg
```bash
apt-get update
apt-get upgrade ffmpeg
```

### Updating Python Wrapper
```bash
pip install --upgrade ffmpeg-python
# Update requirements.txt with new version
```

### Cleanup Old Files
```bash
# Remove processed videos older than 7 days
find /app/backend/processed -name "*.mp4" -mtime +7 -delete

# Clean temporary files
find /app/backend/processed -name "*_subtitle_*.mp4" -delete
find /app/backend/processed -name "*_transition_*.mp4" -delete
```

## Additional Resources

- FFmpeg Documentation: https://ffmpeg.org/documentation.html
- ffmpeg-python GitHub: https://github.com/kkroening/ffmpeg-python
- Video processing examples: `/app/backend/agents/video_tools.py`

## Current Status

✅ **FFmpeg binary**: Installed (v5.1.7)
✅ **ffmpeg-python**: Installed (v0.2.0)
✅ **Requirements.txt**: Updated
✅ **Video tools**: Functional
✅ **Assembly service**: Operational

Last verified: $(date)
