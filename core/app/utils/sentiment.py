import os
import re
import torch
from collections import Counter
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "wonrax/phobert-base-vietnamese-sentiment"
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """Load the PhoBERT sentiment analysis model"""
        try:
            from transformers import pipeline

            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            from transformers import pipeline

            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=-1
            )

    def preprocess_text(self, text: str) -> str:
        """Preprocess Vietnamese text for better sentiment analysis"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Handle emojis (keep them as they can indicate sentiment)
        # Basic emoji normalization could be added here

        # Remove excessive punctuation
        text = re.sub(r'[.!?]{2,}', '.', text)

        return text

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        if not self.pipeline:
            raise Exception("Model not loaded")

        processed_text = self.preprocess_text(text)

        result = self.pipeline(processed_text)[0]

        # Map model outputs to our labels
        label_mapping = {
            'NEG': 'NEGATIVE',
            'NEU': 'NEUTRAL',
            'POS': 'POSITIVE'
        }

        return {
            'label': label_mapping.get(result['label'], 'err'),
            'confidence': float(result['score']),
            'text': text
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment of multiple texts"""
        if not self.pipeline:
            raise Exception("Model not loaded")

        processed_texts = [self.preprocess_text(text) for text in texts]

        results = self.pipeline(processed_texts)

        label_mapping = {
            'NEG': 'NEGATIVE',
            'NEU': 'NEUTRAL',
            'POS': 'POSITIVE'
        }

        return [
            {
                'label': label_mapping.get(result['label'], 'ERR'),
                'confidence': float(result['score']),
                'text': text
            }
            for result, text in zip(results, texts)
        ]

    def extract_keywords(self, texts: List[str], top_n: int = 10) -> List[Dict[str, int]]:
        """Extract most common keywords from texts (basic implementation)"""
        from collections import Counter
        # import jieba

        # Simple Vietnamese word segmentation (you might want to use a better library)
        all_words = []
        for text in texts:
            # Basic tokenization - in production, use proper Vietnamese NLP tools
            words = text.lower().split()
            # Remove common Vietnamese stop words
            stop_words = {'là', 'và', 'của', 'có', 'được', 'cho', 'với', 'trong', 'lên', 'như'}
            words = [word for word in words if word not in stop_words and len(word) > 1]
            all_words.extend(words)

        word_counts = Counter(all_words)
        return [
            {'word': word, 'count': count}
            for word, count in word_counts.most_common(top_n)
        ]

# Global instance

class FakeSentimentAnalyzer:
    def __init__(self):
        self.pipeline = None

    def preprocess_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[.!?]{2,}', '.', text)
        return text

    def _score_label(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        positive_tokens = [
            'tuyệt vời', 'rất tốt', 'tốt', 'xuất sắc', 'yêu', 'thích', 'ok', 'đẹp', 'hài lòng', 'sạch', 'trên cả'
        ]
        negative_tokens = [
            'không hài lòng', 'tệ', 'xấu', 'hỏng', 'chậm', 'đau', 'lỗi', 'không', 'kém', 'dở', 'bực'
        ]
        positive_score = sum(text_lower.count(token) for token in positive_tokens)
        negative_score = sum(text_lower.count(token) for token in negative_tokens)

        if positive_score > negative_score:
            return {'label': 'POSITIVE', 'score': min(0.98, 0.6 + 0.15 * positive_score)}
        if negative_score > positive_score:
            return {'label': 'NEGATIVE', 'score': min(0.98, 0.6 + 0.15 * negative_score)}

        return {'label': 'NEUTRAL', 'score': 0.75 if text_lower else 0.55}

    def analyze_text(self, text: str) -> Dict[str, Any]:
        processed_text = self.preprocess_text(text)
        result = self._score_label(processed_text)
        return {
            'label': result['label'],
            'confidence': float(result['score']),
            'text': text
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.analyze_text(text) for text in texts]

    def extract_keywords(self, texts: List[str], top_n: int = 10) -> List[Dict[str, int]]:
        all_words = []
        stop_words = {'là', 'và', 'của', 'có', 'được', 'cho', 'với', 'trong', 'lên', 'như'}

        for text in texts:
            words = text.lower().split()
            words = [word for word in words if word not in stop_words and len(word) > 1]
            all_words.extend(words)

        word_counts = Counter(all_words)
        return [
            {'word': word, 'count': count}
            for word, count in word_counts.most_common(top_n)
        ]


def _use_fake_analyzer() -> bool:
    env_value = os.getenv('USE_FAKE_SENTIMENT_ANALYZER', 'cokacola').strip().lower()
    print(f"USE_FAKE_SENTIMENT_ANALYZER: '{env_value}'")
    if env_value in {'1', 'true', 'yes', 'y'}:
        return True
    return False

if _use_fake_analyzer():
    print('Using fake SentimentAnalyzer for development')
    sentiment_analyzer = FakeSentimentAnalyzer()
else:
    print("hell Nah")
    sentiment_analyzer = SentimentAnalyzer()