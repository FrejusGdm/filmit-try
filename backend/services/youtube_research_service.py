"""
YouTube Research Service - Analyzes viral videos using YouTube API and GPT-4.
Extracts video metadata, transcripts, and generates AI-powered structure analysis.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from emergentintegrations.llm.chat import LlmChat, UserMessage
from vectra_py.local_index import LocalIndex
from pathlib import Path
from google.cloud import aiplatform
from google.cloud.aiplatform_v1.types import content as gca_content
import google.auth

logger = logging.getLogger(__name__)


class YouTubeResearchService:
    """Service for researching viral video formats from YouTube"""
    
    def __init__(self, youtube_api_key: str, emergent_llm_key: str):
        self.youtube_api_key = youtube_api_key
        self.emergent_llm_key = emergent_llm_key
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        
        # Initialize Vectra index
        self.index_path = Path(__file__).parent.parent / "viral_formats_index"
        self.index_path.mkdir(exist_ok=True)
        self.index = LocalIndex(str(self.index_path))
        
        # Initialize Google Vertex AI for embeddings
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'filmit-477707')
        self.location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
        aiplatform.init(project=self.project_id, location=self.location)
        
        logger.info("YouTube Research Service initialized with Vertex AI embeddings")
    
    def initialize_index(self):
        """Initialize or load the Vectra index"""
        try:
            if not self.index.is_index_created():
                self.index.create_index()
                logger.info("Created new Vectra index for viral formats")
            else:
                logger.info("Loaded existing Vectra index")
        except Exception as e:
            logger.error(f"Error initializing Vectra index: {e}")
            raise
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/shorts\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If no pattern matches, assume it's already a video ID
        if re.match(r'^[A-Za-z0-9_-]{11}$', url):
            return url
        
        return None
    
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """Fetch video metadata from YouTube Data API"""
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"Video not found: {video_id}")
            
            video = response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']
            content_details = video['contentDetails']
            
            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'duration': content_details.get('duration', ''),
                'tags': snippet.get('tags', []),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'thumbnails': snippet.get('thumbnails', {}),
                'category_id': snippet.get('categoryId', '')
            }
        except Exception as e:
            logger.error(f"Error fetching video metadata: {e}")
            raise
    
    def get_video_transcript(self, video_id: str) -> Optional[str]:
        """Fetch video transcript if available"""
        try:
            transcript_list = YouTubeTranscriptApi().fetch(video_id)
            # transcript_list is a list of FetchedTranscriptSnippet objects
            # Access 'text' attribute directly
            transcript = ' '.join([item.text for item in transcript_list])
            return transcript
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"Transcript not available for video {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            return None
    
    async def analyze_video_with_ai(self, metadata: Dict[str, Any], transcript: Optional[str]) -> Dict[str, Any]:
        """Use GPT-4 to analyze video structure, editing patterns, and viral elements"""
        
        # Prepare context for AI analysis
        context = f"""
Analyze this YouTube video and extract its viral format structure and patterns.

**Video Metadata:**
- Title: {metadata['title']}
- Description: {metadata['description'][:500]}...
- Tags: {', '.join(metadata['tags'][:10])}
- Duration: {metadata['duration']}
- Views: {metadata['view_count']:,}
- Likes: {metadata['like_count']:,}
- Comments: {metadata['comment_count']:,}
- Channel: {metadata['channel_title']}

**Transcript (First 2000 chars):**
{transcript[:2000] if transcript else 'Not available - analyze based on metadata only'}

**Analysis Required:**
Provide a comprehensive analysis in JSON format with the following structure:

{{
    "format_name": "A catchy name for this viral format",
    "format_description": "2-3 sentence description of what makes this format work",
    "video_structure": [
        {{"segment": "hook/intro/problem/solution/demo/cta", "timestamp": "0:00-0:05", "description": "what happens in this segment", "duration_seconds": 5}},
        // ... more segments
    ],
    "editing_patterns": {{
        "pacing": "fast/medium/slow with description",
        "cuts_per_minute": "estimated number",
        "transition_style": "cuts/fades/zooms/etc",
        "visual_style": "talking head/screen recording/b-roll/mixed"
    }},
    "engagement_tactics": [
        "List specific tactics: text overlays, music choices, personality, humor, urgency, social proof, etc."
    ],
    "hook_strategy": "How the video captures attention in first 3-5 seconds",
    "platform_fit": ["YouTube", "TikTok", "Instagram", "LinkedIn"],
    "content_type": "tutorial/demo/transformation/educational/entertainment",
    "target_audience": "who this format works best for",
    "viral_elements": [
        "What makes this shareable/viral: relatability, novelty, emotion, value, etc."
    ],
    "success_metrics": {{
        "view_to_like_ratio": {metadata['like_count'] / max(metadata['view_count'], 1) * 100:.2f},
        "engagement_rate": "calculated from available metrics",
        "viral_score": "0-100 based on performance"
    }},
    "key_takeaways": [
        "3-5 actionable insights creators can apply"
    ]
}}

Be specific and actionable. Focus on patterns that can be replicated.
"""
        
        try:
            # Use GPT-4 for analysis
            llm = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"video_analysis_{metadata['video_id']}",
                system_message="You are an expert video analyst specializing in viral content formats and engagement patterns."
            ).with_model("openai", "gpt-4")
            
            response = await llm.send_message(UserMessage(text=context))
            
            # Extract JSON from response
            response_text = response if isinstance(response, str) else response.get('content', '')
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                analysis = json.loads(json_match.group(0))
            else:
                # If no JSON found, wrap the response
                analysis = {
                    "format_name": metadata['title'],
                    "raw_analysis": response_text
                }
            
            # Add metadata to analysis
            analysis['video_id'] = metadata['video_id']
            analysis['video_url'] = f"https://www.youtube.com/watch?v={metadata['video_id']}"
            analysis['analyzed_at'] = datetime.now(timezone.utc).isoformat()
            analysis['source_metadata'] = metadata
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video with AI: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Google Vertex AI"""
        try:
            # Truncate text if too long (Vertex AI has limits)
            max_chars = 3000
            if len(text) > max_chars:
                text = text[:max_chars]
            
            # Load credentials explicitly
            from google.oauth2 import service_account
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            
            # Use the newer prediction API
            # Try text-embedding-004 which is the latest model
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/text-embedding-004"
            
            # Create prediction client with explicit credentials
            from google.cloud import aiplatform_v1
            client = aiplatform_v1.PredictionServiceClient(
                credentials=credentials,
                client_options={"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
            )
            
            # Prepare the request
            instances = [{"content": text}]
            response = client.predict(endpoint=endpoint, instances=instances)
            
            # Extract embedding from response
            embedding = response.predictions[0]['embeddings']['values']
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def store_viral_format(self, analysis: Dict[str, Any]):
        """Store analyzed viral format in Vectra index"""
        try:
            # Create searchable text from analysis
            searchable_text = f"""
            Format: {analysis.get('format_name', '')}
            Description: {analysis.get('format_description', '')}
            Content Type: {analysis.get('content_type', '')}
            Target Audience: {analysis.get('target_audience', '')}
            Platform Fit: {', '.join(analysis.get('platform_fit', []))}
            Engagement Tactics: {', '.join(analysis.get('engagement_tactics', []))}
            Hook Strategy: {analysis.get('hook_strategy', '')}
            Viral Elements: {', '.join(analysis.get('viral_elements', []))}
            Key Takeaways: {', '.join(analysis.get('key_takeaways', []))}
            """
            
            # Generate embedding
            embedding = await self.generate_embedding(searchable_text)
            
            # Store in Vectra (sync operation)
            self.index.insert_item({
                'vector': embedding,
                'metadata': {
                    'video_id': analysis['video_id'],
                    'video_url': analysis['video_url'],
                    'format_name': analysis.get('format_name', ''),
                    'format_description': analysis.get('format_description', ''),
                    'content_type': analysis.get('content_type', ''),
                    'platform_fit': json.dumps(analysis.get('platform_fit', [])),
                    'viral_score': str(analysis.get('success_metrics', {}).get('viral_score', 0)),
                    'analyzed_at': analysis['analyzed_at']
                }
            })
            
            logger.info(f"Stored viral format: {analysis.get('format_name')} ({analysis['video_id']})")
            
            # Also store full analysis as JSON file
            analysis_file = self.index_path / f"{analysis['video_id']}_full.json"
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error storing viral format: {e}")
            raise
    
    async def search_viral_formats(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for viral formats using semantic search"""
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query)
            
            # Search in Vectra (sync operation)
            results = self.index.query_items(query_embedding, top_k)
            
            # Load full analysis for each result
            enriched_results = []
            for result in results:
                video_id = result['item']['metadata']['video_id']
                analysis_file = self.index_path / f"{video_id}_full.json"
                
                if analysis_file.exists():
                    with open(analysis_file, 'r') as f:
                        full_analysis = json.load(f)
                    
                    enriched_results.append({
                        'score': result['score'],
                        'video_id': video_id,
                        'format_name': result['item']['metadata']['format_name'],
                        'format_description': result['item']['metadata']['format_description'],
                        'full_analysis': full_analysis
                    })
                else:
                    enriched_results.append({
                        'score': result['score'],
                        'metadata': result['item']['metadata']
                    })
            
            return enriched_results
            
        except Exception as e:
            logger.error(f"Error searching viral formats: {e}")
            raise
    
    async def research_video(self, video_url: str) -> Dict[str, Any]:
        """Full pipeline: fetch metadata, transcript, analyze, and store"""
        try:
            # Extract video ID
            video_id = self.extract_video_id(video_url)
            if not video_id:
                raise ValueError(f"Invalid YouTube URL: {video_url}")
            
            logger.info(f"Researching video: {video_id}")
            
            # Fetch metadata
            metadata = self.get_video_metadata(video_id)
            logger.info(f"Fetched metadata for: {metadata['title']}")
            
            # Fetch transcript
            transcript = self.get_video_transcript(video_id)
            if transcript:
                logger.info(f"Fetched transcript ({len(transcript)} chars)")
            else:
                logger.info("No transcript available, analyzing from metadata only")
            
            # Analyze with AI
            analysis = await self.analyze_video_with_ai(metadata, transcript)
            logger.info(f"Completed AI analysis: {analysis.get('format_name')}")
            
            # Store in vector database
            await self.store_viral_format(analysis)
            logger.info("Stored in vector database")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error researching video: {e}")
            raise


# Global service instance
youtube_research_service: Optional[YouTubeResearchService] = None


def get_youtube_research_service() -> YouTubeResearchService:
    """Get or create the YouTube research service instance"""
    global youtube_research_service
    
    if youtube_research_service is None:
        youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
        emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if not youtube_api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment")
        if not emergent_llm_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        youtube_research_service = YouTubeResearchService(
            youtube_api_key=youtube_api_key,
            emergent_llm_key=emergent_llm_key
        )
    
    return youtube_research_service
