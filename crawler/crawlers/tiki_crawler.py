import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
import re

class TikiCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Tiki URL"""
        # Tiki URLs typically look like: https://tiki.vn/product-p123456.html
        match = re.search(r'/product-p(\d+)\.html', url)
        if match:
            return match.group(1)
        return None

    def get_reviews(self, product_url: str, max_reviews: int = 50) -> List[Dict]:
        """
        Crawl reviews from a Tiki product
        Note: This is a basic implementation. Tiki may have anti-scraping measures.
        """
        product_id = self.extract_product_id(product_url)
        if not product_id:
            raise ValueError("Invalid Tiki product URL")

        reviews = []

        try:
            # This is a simplified version - Tiki uses complex APIs
            # For demo purposes, return mock data

            mock_reviews = [
                {
                    'text': 'Sản phẩm chính hãng, chất lượng tuyệt vời',
                    'rating': 5,
                    'author': 'Nguyễn Văn A',
                    'timestamp': '2024-01-01T10:00:00Z'
                },
                {
                    'text': 'Giao hàng đúng hẹn, phục vụ tốt',
                    'rating': 4,
                    'author': 'Trần Thị B',
                    'timestamp': '2024-01-01T11:00:00Z'
                },
                {
                    'text': 'Sản phẩm không đúng như mô tả, thất vọng',
                    'rating': 2,
                    'author': 'Lê Văn C',
                    'timestamp': '2024-01-01T12:00:00Z'
                },
                {
                    'text': 'Giá rẻ, chất lượng ổn, sẽ ủng hộ shop',
                    'rating': 4,
                    'author': 'Phạm Thị D',
                    'timestamp': '2024-01-01T13:00:00Z'
                }
            ]

            reviews = mock_reviews[:max_reviews]

        except Exception as e:
            print(f"Error crawling Tiki reviews: {e}")

        return reviews

    def get_product_info(self, product_url: str) -> Dict:
        """Get basic product information"""
        product_id = self.extract_product_id(product_url)
        if not product_id:
            raise ValueError("Invalid Tiki product URL")

        # Mock product info
        return {
            'product_id': product_id,
            'name': 'Sample Product',
            'price': 150000,
            'rating': 4.2,
            'total_reviews': 80
        }