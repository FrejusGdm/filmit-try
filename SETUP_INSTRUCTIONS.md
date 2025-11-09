# Filmit! Setup Instructions

## Quick Start (New Environment)

If you're setting up Filmit! in a new Emergent instance or fresh environment, run:

```bash
cd /app
./setup.sh
```

This will automatically install all system dependencies including FFmpeg.

---

## Manual Setup

### 1. System Dependencies

**FFmpeg (Required for Video Assembly)**

FFmpeg is required for video processing features (merging clips, adding transitions, subtitles).

```bash
# Update package lists
apt-get update

# Install FFmpeg
apt-get install -y ffmpeg

# Verify installation
ffmpeg -version
ffprobe -version
```

### 2. Python Dependencies

```bash
cd /app/backend
pip install -r requirements.txt
```

### 3. Node Dependencies

```bash
cd /app/frontend
yarn install
```

### 4. Create Required Directories

```bash
mkdir -p /app/backend/uploads
mkdir -p /app/backend/processed
chmod 755 /app/backend/uploads
chmod 755 /app/backend/processed
```

### 5. Restart Services

```bash
sudo supervisorctl restart all
```

---

## Troubleshooting

### Error: "No such file or directory: '/usr/bin/ffmpeg'"

**Problem:** FFmpeg is not installed on the system.

**Solution:**
```bash
# Option 1: Run setup script
/app/setup.sh

# Option 2: Manual installation
apt-get update && apt-get install -y ffmpeg

# Restart backend
sudo supervisorctl restart backend
```

### Error: "Assembly failed: Merge failed"

**Problem:** FFmpeg installation incomplete or missing.

**Solution:**
```bash
# Verify FFmpeg is installed
which ffmpeg
ffmpeg -version

# If not found, install it
apt-get update && apt-get install -y ffmpeg

# Restart services
sudo supervisorctl restart all
```

### Error: "Cannot find module 'ffmpeg'"

**Problem:** Python ffmpeg-python package not installed.

**Solution:**
```bash
cd /app/backend
pip install ffmpeg-python==0.2.0
pip freeze > requirements.txt
sudo supervisorctl restart backend
```

---

## Verification

Run the verification script to check all dependencies:

```bash
/app/verify_ffmpeg.sh
```

Expected output:
```
✅ FFmpeg binary found
✅ FFprobe binary found
✅ ffmpeg-python module installed
✅ Python integration working
✅ video_tools.py ready
```

---

## Environment-Specific Notes

### Emergent Platform

When creating a new instance on Emergent:
1. The setup script should run automatically (if configured)
2. If not, manually run `/app/setup.sh`
3. Check supervisor logs: `tail -f /var/log/supervisor/backend.err.log`

### Docker/Containerized Environments

Add to your Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -r /app/backend/requirements.txt
```

### Local Development

Ensure FFmpeg is installed on your system:
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `apt-get install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/download.html

---

## System Requirements

### Minimum Requirements
- **Python**: 3.11+
- **Node.js**: 18+
- **MongoDB**: 4.4+
- **FFmpeg**: 4.0+ (5.1+ recommended)
- **Disk Space**: 5GB+ for video processing
- **RAM**: 2GB+ (4GB+ recommended for video assembly)

### Recommended Requirements
- **Python**: 3.11
- **Node.js**: 20
- **MongoDB**: 6.0+
- **FFmpeg**: 5.1+
- **Disk Space**: 20GB+
- **RAM**: 8GB+

---

## Service Management

### Check Service Status
```bash
sudo supervisorctl status
```

### Restart All Services
```bash
sudo supervisorctl restart all
```

### Restart Individual Services
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### View Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log

# Frontend logs
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

---

## File Locations

### Application
- **Root**: `/app/`
- **Backend**: `/app/backend/`
- **Frontend**: `/app/frontend/`

### Data
- **Uploads**: `/app/backend/uploads/` (user-uploaded video segments)
- **Processed**: `/app/backend/processed/` (assembled videos)
- **Database**: MongoDB (configured via MONGO_URL env var)

### Configuration
- **Backend Env**: `/app/backend/.env`
- **Frontend Env**: `/app/frontend/.env`
- **Requirements**: `/app/backend/requirements.txt`
- **Package**: `/app/frontend/package.json`

### Scripts
- **Setup**: `/app/setup.sh` - Full environment setup
- **Verify FFmpeg**: `/app/verify_ffmpeg.sh` - Check FFmpeg installation
- **System Dependencies**: `/app/scripts/install_system_dependencies.sh`

---

## Common Issues and Solutions

### 1. Video Assembly Fails

**Symptoms:**
- Error message: "Assembly failed: Merge failed"
- Error: "No such file or directory: '/usr/bin/ffmpeg'"

**Solution:**
```bash
# Install FFmpeg
apt-get update && apt-get install -y ffmpeg

# Verify
ffmpeg -version

# Restart backend
sudo supervisorctl restart backend
```

### 2. Backend Won't Start

**Check logs:**
```bash
tail -n 100 /var/log/supervisor/backend.err.log
```

**Common causes:**
- Missing Python packages → Run `pip install -r requirements.txt`
- Port already in use → Check if another process is using port 8001
- Database connection issues → Verify MONGO_URL in backend/.env

### 3. Frontend Build Errors

**Solution:**
```bash
cd /app/frontend
rm -rf node_modules
yarn install
sudo supervisorctl restart frontend
```

### 4. Permission Issues

**Solution:**
```bash
# Fix upload/processed directory permissions
chmod 755 /app/backend/uploads
chmod 755 /app/backend/processed

# Ensure backend can write to these directories
chown -R www-data:www-data /app/backend/uploads
chown -R www-data:www-data /app/backend/processed
```

---

## Security Best Practices

### 1. Environment Variables

Never commit `.env` files with sensitive data:
```bash
# Backend .env should contain:
MONGO_URL=mongodb://localhost:27017/filmit
EMERGENT_LLM_KEY=your-key-here  # Keep this secret!
JWT_SECRET_KEY=random-secret-key  # Generate unique per environment
```

### 2. File Uploads

Uploaded files are stored in `/app/backend/uploads/`:
- Maximum file size should be enforced (currently handled by frontend)
- File type validation in place (video/* only)
- Files named with project ID to prevent overwrites

### 3. Video Processing

FFmpeg commands run with limited privileges:
- No shell injection vulnerabilities (using ffmpeg-python library)
- Input validation on file paths
- Temporary files cleaned up after assembly

### 4. Database

MongoDB access should be restricted:
- Use authentication in production
- Limit connection to localhost if possible
- Regular backups recommended

---

## Performance Tips

### 1. Video Assembly Optimization

- Use simple concatenation (no transitions) for faster assembly
- Limit subtitle processing to essential shots
- Choose appropriate platform optimization (smaller resolution = faster)

### 2. Disk Space Management

Clean up old processed videos regularly:
```bash
# Remove videos older than 7 days
find /app/backend/processed -name "*.mp4" -mtime +7 -delete
```

### 3. Memory Management

Large video files can consume significant memory:
- Monitor with `htop` or `top`
- Restart backend periodically if memory usage grows
- Consider limiting concurrent assembly jobs

---

## Support Resources

### Documentation
- **FFmpeg Setup**: `/app/FFMPEG_SETUP.md`
- **Video Tools**: `/app/backend/agents/video_tools.py`
- **API Documentation**: Run backend and visit `/docs`

### Verification Scripts
- `/app/setup.sh` - Complete setup
- `/app/verify_ffmpeg.sh` - FFmpeg verification
- `/app/test_auth_flow.py` - Test authentication

### Logs
- Backend: `/var/log/supervisor/backend.*.log`
- Frontend: `/var/log/supervisor/frontend.*.log`
- Supervisor: `/var/log/supervisor/supervisord.log`

---

## Quick Reference

```bash
# Setup new environment
/app/setup.sh

# Verify FFmpeg
/app/verify_ffmpeg.sh

# Check services
sudo supervisorctl status

# Restart everything
sudo supervisorctl restart all

# View backend logs
tail -f /var/log/supervisor/backend.err.log

# Test backend health
curl http://localhost:8001/api/health
```

---

## Need Help?

1. Check logs: `tail -f /var/log/supervisor/backend.err.log`
2. Verify FFmpeg: `/app/verify_ffmpeg.sh`
3. Run setup: `/app/setup.sh`
4. Restart services: `sudo supervisorctl restart all`

For persistent issues, check:
- System requirements are met
- All dependencies installed
- Sufficient disk space available
- MongoDB is running and accessible
