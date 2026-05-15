import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

class YouTubeCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.lstrip('/')
        return None

    def get_comments(self, video_url: str, max_comments: int = 50) -> List[Dict]:
        """
        Crawl comments from a YouTube video
        Note: This is a basic implementation. YouTube frequently changes their structure,
        so this might need updates or use official YouTube API for production.
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        comments = []

        try:
            # This is a simplified version - in production, you'd want to use YouTube API
            # or more sophisticated scraping techniques

            # For demo purposes, return mock data
            mock_comments = [
                {
                    'text': 'Video rất hay, cảm ơn bạn đã chia sẻ!',
                    'author': 'User1',
                    'likes': 10,
                    'timestamp': '2024-01-01T10:00:00Z'
                },
                {
                    'text': 'Nội dung chất lượng, sẽ theo dõi channel này',
                    'author': 'User2',
                    'likes': 5,
                    'timestamp': '2024-01-01T11:00:00Z'
                },
                {
                    'text': 'Không hài lòng với chất lượng video',
                    'author': 'User3',
                    'likes': 1,
                    'timestamp': '2024-01-01T12:00:00Z'
                }
            ]

            comments = mock_comments[:max_comments]

        except Exception as e:
            print(f"Error crawling YouTube comments: {e}")

        return comments

    def get_video_info(self, video_url: str) -> Dict:
        """Get basic video information"""
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        # Mock video info - in production, use YouTube API
        return {
            'video_id': video_id,
            'title': 'Sample Video Title',
            'channel': 'Sample Channel',
            'view_count': 1000,
            'like_count': 100
        }