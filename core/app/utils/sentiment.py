from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
from typing import List, Dict, Any

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
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to CPU
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
sentiment_analyzer = SentimentAnalyzer()