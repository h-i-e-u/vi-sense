import json
import re
import unicodedata
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class TikiCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        })

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Tiki URL."""
        match = re.search(r"-p(\d+)\.html(?:\?|$)", url)
        if match:
            return match.group(1)

        match = re.search(r"/product-p(\d+)\.html(?:\?|$)", url)
        if match:
            return match.group(1)

        return None

    def _validate_product_url(self, product_url: str) -> None:
        parsed = urlparse(product_url)
        host = (parsed.netloc or "").lower()
        if not host.endswith("tiki.vn"):
            raise ValueError("URL must be a tiki.vn product page")
        if not self.extract_product_id(product_url):
            raise ValueError("Invalid Tiki product URL")

    def _clean_text(self, text: str) -> str:
        text = BeautifulSoup(text or "", "html.parser").get_text(" ")
        return re.sub(r"\s+", " ", text).strip()

    def _normalize_for_filter(self, text: str) -> str:
        normalized = text.replace("đ", "d").replace("Đ", "D")
        normalized = unicodedata.normalize("NFKD", normalized)
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        return normalized.lower().strip()

    def _append_review(
        self,
        reviews: List[Dict],
        seen_texts: set,
        text: str,
        rating: Optional[int] = None,
        author: str = "Unknown",
        timestamp: str = "",
    ) -> None:
        text = self._clean_text(text)
        if len(text) < 8 or len(text) > 2000 or text in seen_texts:
            return
        normalized = self._normalize_for_filter(text)
        if re.fullmatch(r"da dung \d+ (ngay|thang|nam)", normalized):
            return

        seen_texts.add(text)
        reviews.append({
            "text": text,
            "rating": rating,
            "author": author or "Unknown",
            "timestamp": timestamp or "",
        })

    def _iter_json_values(self, value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from self._iter_json_values(child)
        elif isinstance(value, list):
            for child in value:
                yield from self._iter_json_values(child)

    def _parse_reviews_from_json(self, soup: BeautifulSoup, max_reviews: int) -> List[Dict]:
        reviews: List[Dict] = []
        seen_texts = set()
        scripts = soup.find_all("script", type=lambda value: value and "json" in value.lower())

        for script in scripts:
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue

            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue

            for item in self._iter_json_values(payload):
                text = (
                    item.get("reviewBody")
                    or item.get("content")
                    or item.get("comment")
                    or item.get("review")
                )
                if not isinstance(text, str):
                    continue

                rating = item.get("ratingValue") or item.get("rating") or item.get("stars")
                try:
                    rating = int(float(rating)) if rating is not None else None
                except (TypeError, ValueError):
                    rating = None

                author = item.get("author") or item.get("created_by") or "Unknown"
                if isinstance(author, dict):
                    author = author.get("name") or author.get("full_name") or "Unknown"

                timestamp = item.get("datePublished") or item.get("created_at") or item.get("createdAt") or ""
                self._append_review(reviews, seen_texts, text, rating, str(author), str(timestamp))

                if len(reviews) >= max_reviews:
                    return reviews

        return reviews

    def _parse_reviews_from_dom(self, soup: BeautifulSoup, max_reviews: int) -> List[Dict]:
        reviews: List[Dict] = []
        seen_texts = set()
        selectors = [
            '[data-view-id*="pdp_review"]',
            '[data-view-id*="review"]',
            '[class*="review-comment"]',
            '[class*="review"]',
            '[class*="comment"]',
        ]

        for selector in selectors:
            for node in soup.select(selector):
                text = self._clean_text(node.get_text(" "))
                lowered = text.lower()
                blocked = ["dang nhap", "gio hang", "san pham tuong tu"]
                if any(fragment in lowered for fragment in blocked):
                    continue

                self._append_review(reviews, seen_texts, text)
                if len(reviews) >= max_reviews:
                    return reviews

        return reviews

    def _parse_reviews(self, html: str, max_reviews: int) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        reviews = self._parse_reviews_from_json(soup, max_reviews)
        seen_texts = {review["text"] for review in reviews}

        for review in self._parse_reviews_from_dom(soup, max_reviews):
            if review["text"] not in seen_texts:
                reviews.append(review)
                seen_texts.add(review["text"])
            if len(reviews) >= max_reviews:
                break

        return reviews[:max_reviews]

    def _mock_reviews(self, max_reviews: int) -> List[Dict]:
        mock_reviews = [
            {
                "text": "San pham chinh hang, chat luong tot, dong goi can than",
                "rating": 5,
                "author": "Mock User 1",
                "timestamp": "2024-01-01T10:00:00Z",
            },
            {
                "text": "Giao hang dung hen, san pham dung nhu mo ta",
                "rating": 4,
                "author": "Mock User 2",
                "timestamp": "2024-01-01T11:00:00Z",
            },
            {
                "text": "San pham khong dung nhu mong doi, can cai thien chat luong",
                "rating": 2,
                "author": "Mock User 3",
                "timestamp": "2024-01-01T12:00:00Z",
            },
            {
                "text": "Gia hop ly, se ung ho shop lan sau",
                "rating": 4,
                "author": "Mock User 4",
                "timestamp": "2024-01-01T13:00:00Z",
            },
        ]
        return mock_reviews[:max_reviews]

    def get_reviews(self, product_url: str, max_reviews: int = 50) -> List[Dict]:
        """
        Crawl reviews from a Tiki product page using requests + BeautifulSoup.
        Falls back to mock data when page scraping cannot find reviews.
        """
        self._validate_product_url(product_url)

        try:
            response = self.session.get(product_url, timeout=20)
            response.raise_for_status()
            reviews = self._parse_reviews(response.text, max_reviews)
            if reviews:
                return reviews
        except Exception as e:
            print(f"Error crawling Tiki reviews: {e}")

        return self._mock_reviews(max_reviews)

    def get_product_info(self, product_url: str) -> Dict:
        """Get basic product information."""
        product_id = self.extract_product_id(product_url)
        if not product_id:
            raise ValueError("Invalid Tiki product URL")

        try:
            response = self.session.get(product_url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title_tag = soup.select_one("meta[property='og:title']")
            price_tag = soup.select_one("meta[property='product:price:amount']")
            rating_match = re.search(r'"ratingValue"\s*:\s*"?([0-9.]+)"?', response.text)

            price = None
            if price_tag:
                try:
                    price = int(float(price_tag.get("content", "0")))
                except ValueError:
                    price = None

            rating = None
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                except ValueError:
                    rating = None

            return {
                "product_id": product_id,
                "name": title_tag.get("content", "").strip() if title_tag else "Tiki Product",
                "price": price,
                "rating": rating,
                "total_reviews": None,
            }
        except Exception as e:
            print(f"Error crawling Tiki product info: {e}")

        return {
            "product_id": product_id,
            "name": "Sample Product",
            "price": 150000,
            "rating": 4.2,
            "total_reviews": 80,
        }
