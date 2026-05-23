import os
import time
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Retry configuration
MAX_RETRIES = 3
BASE_BACKOFF = 1  # seconds


class YouTubeCrawler:
    """YouTube crawler using Google API Python Client"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTubeCrawler with API key"""
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY is required for YouTube Data API access")
        
        self.youtube = build(
            "youtube", 
            "v3", 
            developerKey=self.api_key,
            cache_discovery=False  # Disable cache to avoid issues
        )

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        parsed_url = urlparse(url)
        hostname = (parsed_url.hostname or "").lower()

        if hostname in ["www.youtube.com", "youtube.com", "m.youtube.com"]:
            if parsed_url.path == "/watch":
                return parse_qs(parsed_url.query).get("v", [None])[0]
            if parsed_url.path.startswith("/shorts/"):
                return parsed_url.path.split("/shorts/")[1].split("/")[0]
        elif hostname == "youtu.be":
            return parsed_url.path.lstrip("/")

        return None

    def _execute_with_retry(self, request):
        """Execute API request with retry logic and exponential backoff"""
        for attempt in range(MAX_RETRIES):
            try:
                return request.execute()
            except HttpError as e:
                # Check if it's a quota error (403) or server error (5xx)
                if e.resp.status in [403, 500, 502, 503, 504]:
                    if attempt < MAX_RETRIES - 1:
                        wait_time = BASE_BACKOFF * (2 ** attempt)
                        print(f"API error (status {e.resp.status}). Retrying in {wait_time}s... (attempt {attempt + 1}/{MAX_RETRIES})")
                        time.sleep(wait_time)
                        continue
                raise
            except Exception as e:
                # Handle timeout and connection errors
                if attempt < MAX_RETRIES - 1:
                    wait_time = BASE_BACKOFF * (2 ** attempt)
                    print(f"Connection error: {str(e)}. Retrying in {wait_time}s... (attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(wait_time)
                    continue
                raise
        
        raise Exception("Max retries exceeded")

    def get_comments(self, video_url: str, max_comments: int = 50) -> List[Dict]:
        """
        Fetch comments from a YouTube video using the YouTube Data API.
        
        Args:
            video_url: YouTube video URL
            max_comments: Maximum number of comments to fetch
            
        Returns:
            List of comment dictionaries with text, author, likes, and timestamp
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        comments: List[Dict] = []
        page_token: Optional[str] = None

        try:
            while len(comments) < max_comments:
                request = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="plainText",
                    maxResults=min(100, max_comments - len(comments)),
                    pageToken=page_token,
                    order="relevance"
                )
                
                response = self._execute_with_retry(request)
                items = response.get("items", [])

                if not items:
                    break

                for item in items:
                    snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                    comment_text = snippet.get("textDisplay", "").strip()
                    
                    if comment_text:
                        comments.append({
                            "text": comment_text,
                            "author": snippet.get("authorDisplayName", "Unknown"),
                            "likes": int(snippet.get("likeCount", 0)),
                            "timestamp": snippet.get("publishedAt", "")
                        })

                    if len(comments) >= max_comments:
                        break

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

                # Add small delay between requests to avoid rate limiting
                time.sleep(0.1)

        except HttpError as e:
            error_msg = e.content.decode() if hasattr(e, 'content') else str(e)
            raise ValueError(f"YouTube API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Error fetching comments: {str(e)}")

        return comments[:max_comments]

    def get_video_info(self, video_url: str) -> Dict:
        """
        Fetch basic video metadata from the YouTube Data API.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Dictionary with video metadata (title, channel, views, likes, etc.)
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        try:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            
            response = self._execute_with_retry(request)
            items = response.get("items", [])

            if not items:
                raise ValueError("Video not found or is unavailable")

            item = items[0]
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})

            return {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "published_at": snippet.get("publishedAt", ""),
                "description": snippet.get("description", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            }

        except HttpError as e:
            error_msg = e.content.decode() if hasattr(e, 'content') else str(e)
            raise ValueError(f"YouTube API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Error fetching video info: {str(e)}")

 