from typing import List, Dict
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class YouTubeService:
    def __init__(self):
        pass
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def get_transcript(self, video_id: str) -> Dict:
        """Get transcript for a YouTube video"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript segments
            full_transcript = " ".join([item['text'] for item in transcript_list])
            
            return {
                "video_id": video_id,
                "transcript": full_transcript,
                "segments": transcript_list
            }
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"Transcript not available for video {video_id}: {e}")
            return None
        except Exception as e:
            print(f"Error getting transcript for video {video_id}: {e}")
            return None
    
    async def search_and_extract(self, query: str) -> List[Dict]:
        """Search for YouTube videos in query and extract transcripts"""
        results = []
        
        # Find YouTube URLs in the query
        youtube_urls = re.findall(
            r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#\s]+)',
            query
        )
        
        for video_id in youtube_urls[:3]:  # Limit to 3 videos
            transcript_data = await self.get_transcript(video_id)
            if transcript_data:
                # Truncate transcript for snippet
                snippet = transcript_data["transcript"][:500] + "..."
                
                results.append({
                    "title": f"YouTube Video Transcript: {video_id}",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "snippet": snippet,
                    "source_type": "youtube",
                    "full_transcript": transcript_data["transcript"]
                })
        
        return results
    
    async def get_transcript_by_url(self, url: str) -> Dict:
        """Get transcript by YouTube URL"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
        
        return await self.get_transcript(video_id)

