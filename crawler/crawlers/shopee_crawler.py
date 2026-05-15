import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
import re

class ShopeeCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Shopee URL"""
        # Shopee URLs typically look like: https://shopee.vn/product/123456789/987654321
        match = re.search(r'/product/(\d+)/(\d+)', url)
        if match:
            return match.group(2)  # item_id
        return None

    def get_reviews(self, product_url: str, max_reviews: int = 50) -> List[Dict]:
        """
        Crawl reviews from a Shopee product
        Note: This is a basic implementation. Shopee may have anti-scraping measures.
        """
        product_id = self.extract_product_id(product_url)
        if not product_id:
            raise ValueError("Invalid Shopee product URL")

        reviews = []

        try:
            # This is a simplified version - Shopee uses complex APIs
            # For demo purposes, return mock data

            mock_reviews = [
                {
                    'text': 'Sản phẩm chất lượng tốt, đóng gói cẩn thận',
                    'rating': 5,
                    'author': 'Nguyễn Văn A',
                    'timestamp': '2024-01-01T10:00:00Z'
                },
                {
                    'text': 'Giao hàng nhanh, sản phẩm đúng như mô tả',
                    'rating': 4,
                    'author': 'Trần Thị B',
                    'timestamp': '2024-01-01T11:00:00Z'
                },
                {
                    'text': 'Sản phẩm bị hỏng, không hài lòng',
                    'rating': 1,
                    'author': 'Lê Văn C',
                    'timestamp': '2024-01-01T12:00:00Z'
                },
                {
                    'text': 'Giá cả hợp lý, sẽ mua lại lần sau',
                    'rating': 5,
                    'author': 'Phạm Thị D',
                    'timestamp': '2024-01-01T13:00:00Z'
                }
            ]

            reviews = mock_reviews[:max_reviews]

        except Exception as e:
            print(f"Error crawling Shopee reviews: {e}")

        return reviews

    def get_product_info(self, product_url: str) -> Dict:
        """Get basic product information"""
        product_id = self.extract_product_id(product_url)
        if not product_id:
            raise ValueError("Invalid Shopee product URL")

        # Mock product info
        return {
            'product_id': product_id,
            'name': 'Sample Product',
            'price': 100000,
            'rating': 4.5,
            'total_reviews': 100
        }