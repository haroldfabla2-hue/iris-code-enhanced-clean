"""
Video Generation API endpoints for VEO3 integration
Handles video generation with limitations (2 times per week)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import os
import json
from pathlib import Path

# Mock VEO3 API integration
class VideoRequest(BaseModel):
    prompt: str
    style: str = "reel"
    duration: int = 30
    aspect_ratio: str = "9:16"
    quality: str = "hd"
    voiceover: bool = False
    music: bool = False
    api_key: str

class VideoResponse(BaseModel):
    video_id: str
    status: str
    prompt: str
    video_url: Optional[str] = None
    duration: Optional[int] = None
    format: str = "mp4"
    created_at: str
    thumbnail_url: Optional[str] = None
    metadata: Optional[dict] = None
    error: Optional[str] = None

class VideoLimitResponse(BaseModel):
    used_count: int
    remaining_count: int
    reset_date: str
    weekly_limit: int = 2

class VideoHistoryResponse(BaseModel):
    videos: List[VideoResponse]

# In-memory storage for video generations
video_generations: dict = {}
user_limits: dict = {}  # Track usage per API key

# Weekly limit tracking
WEEKLY_LIMIT = 2
LIMIT_WINDOW_DAYS = 7

router = APIRouter(prefix="/api/v1/assets/video", tags=["video"])

def check_weekly_limit(api_key: str) -> tuple[bool, int]:
    """Check if user has exceeded weekly limit"""
    now = datetime.now()
    week_start = now - timedelta(days=LIMIT_WINDOW_DAYS)
    
    # Get user's usage in the past week
    user_videos = [
        v for v in video_generations.values() 
        if v.get("api_key") == api_key and 
        datetime.fromisoformat(v["created_at"]) > week_start
    ]
    
    used_count = len(user_videos)
    remaining = max(0, WEEKLY_LIMIT - used_count)
    
    return used_count < WEEKLY_LIMIT, remaining

@router.post("/veo3", response_model=VideoResponse)
async def generate_video_veo3(request: VideoRequest):
    """Generate video using VEO3 API with weekly limit"""
    try:
        # Validate API key
        expected_api_key = "AIzaSyBlqzSr6sv65rsQmNjNMGDZ5sz72DCpP38"
        if request.api_key != expected_api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Check weekly limit
        can_generate, remaining = check_weekly_limit(request.api_key)
        if not can_generate:
            raise HTTPException(
                status_code=429, 
                detail=f"Weekly limit exceeded. {WEEKLY_LIMIT} videos per week. Remaining: 0"
            )
        
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        
        # Create video generation record
        video_record = {
            "video_id": video_id,
            "status": "pending",
            "prompt": request.prompt,
            "format": "mp4",
            "created_at": datetime.now().isoformat(),
            "api_key": request.api_key,
            "parameters": {
                "style": request.style,
                "duration": request.duration,
                "aspect_ratio": request.aspect_ratio,
                "quality": request.quality,
                "voiceover": request.voiceover,
                "music": request.music
            }
        }
        
        video_generations[video_id] = video_record
        
        # Simulate VEO3 API call (in real implementation, this would call VEO3)
        # For now, we'll simulate the process
        await simulate_veo3_generation(video_id, request)
        
        return VideoResponse(
            video_id=video_id,
            status="processing",
            prompt=request.prompt,
            format="mp4",
            created_at=video_record["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@router.get("/veo3/{video_id}/status", response_model=VideoResponse)
async def get_video_status(video_id: str):
    """Get status of video generation"""
    if video_id not in video_generations:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = video_generations[video_id]
    
    return VideoResponse(
        video_id=video["video_id"],
        status=video["status"],
        prompt=video["prompt"],
        video_url=video.get("video_url"),
        duration=video.get("duration"),
        format=video.get("format", "mp4"),
        created_at=video["created_at"],
        thumbnail_url=video.get("thumbnail_url"),
        metadata=video.get("metadata"),
        error=video.get("error")
    )

@router.get("/veo3/limit", response_model=VideoLimitResponse)
async def get_video_generation_limit(api_key: str = "AIzaSyBlqzSr6sv65rsQmNjNMGDZ5sz72DCpP38"):
    """Get current video generation limit status"""
    can_generate, remaining = check_weekly_limit(api_key)
    used = WEEKLY_LIMIT - remaining
    
    # Next reset is next Monday
    now = datetime.now()
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0 and now.weekday() == 0:  # If it's Monday, reset is next week
        days_until_monday = 7
    reset_date = (now + timedelta(days=days_until_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    return VideoLimitResponse(
        used_count=used,
        remaining_count=remaining,
        reset_date=reset_date.isoformat(),
        weekly_limit=WEEKLY_LIMIT
    )

@router.get("/veo3/history", response_model=VideoHistoryResponse)
async def get_video_history(limit: int = 10, api_key: str = "AIzaSyBlqzSr6sv65rsQmNjNMGDZ5sz72DCpP38"):
    """Get video generation history for user"""
    user_videos = [
        v for v in video_generations.values() 
        if v.get("api_key") == api_key
    ]
    
    # Sort by created_at descending and limit
    user_videos.sort(key=lambda x: x["created_at"], reverse=True)
    user_videos = user_videos[:limit]
    
    video_responses = []
    for video in user_videos:
        video_responses.append(VideoResponse(
            video_id=video["video_id"],
            status=video["status"],
            prompt=video["prompt"],
            video_url=video.get("video_url"),
            duration=video.get("duration"),
            format=video.get("format", "mp4"),
            created_at=video["created_at"],
            thumbnail_url=video.get("thumbnail_url"),
            metadata=video.get("metadata"),
            error=video.get("error")
        ))
    
    return VideoHistoryResponse(videos=video_responses)

async def simulate_veo3_generation(video_id: str, request: VideoRequest):
    """Simulate VEO3 video generation process"""
    import asyncio
    
    # Simulate processing time based on duration
    processing_time = min(request.duration * 2, 60)  # Max 60 seconds
    await asyncio.sleep(2)  # Brief delay before starting
    
    # Update status to processing
    video_generations[video_id]["status"] = "processing"
    
    # Simulate completion
    await asyncio.sleep(processing_time)
    
    # Generate mock video URL (in real implementation, this would be VEO3 response)
    video_url = f"https://storage.googleapis.com/iris-assets/videos/{video_id}.mp4"
    thumbnail_url = f"https://storage.googleapis.com/iris-assets/thumbnails/{video_id}.jpg"
    
    # Determine video properties based on request
    width, height = 1080, 1920 if request.aspect_ratio == "9:16" else (1920, 1080 if request.aspect_ratio == "16:9" else (1080, 1080))
    fps = 30
    
    video_generations[video_id].update({
        "status": "completed",
        "video_url": video_url,
        "thumbnail_url": thumbnail_url,
        "duration": request.duration,
        "metadata": {
            "width": width,
            "height": height,
            "fps": fps,
            "duration": request.duration,
            "style": request.style,
            "quality": request.quality
        }
    })

# Cleanup old generations (run periodically)
@router.post("/cleanup")
async def cleanup_old_generations():
    """Clean up old video generations to free memory"""
    now = datetime.now()
    cutoff_date = now - timedelta(days=30)  # Keep for 30 days
    
    to_remove = []
    for video_id, video in video_generations.items():
        video_date = datetime.fromisoformat(video["created_at"])
        if video_date < cutoff_date:
            to_remove.append(video_id)
    
    for video_id in to_remove:
        del video_generations[video_id]
    
    return {"removed_count": len(to_remove), "remaining_count": len(video_generations)}