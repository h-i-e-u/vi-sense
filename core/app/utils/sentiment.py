import os
import re
import threading
import torch
from collections import Counter
from typing import List, Dict, Any
from dotenv import load_dotenv
from app.utils.hybrid_phobert import HybridPhoBERTClassifier
from app.utils.text_preprocess import preprocess_text
from transformers import pipeline, AutoTokenizer
from pathlib import Path


load_dotenv()

# Label mapping
LABEL_MAPPING = {
    'NEG': 'NEGATIVE',
    'NEU': 'NEUTRAL',
    'POS': 'POSITIVE'
}

ID2LABEL = {
    0: 'NEGATIVE',
    1: 'POSITIVE',
    2: 'NEUTRAL'
}

class SentimentAnalyzer:

    def __init__(self):

        self.model_type = os.getenv(
            "SENTIMENT_MODEL",
            "custom"
        ).lower()

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.pipeline = None
        self.tokenizer = None
        self.model = None
        self._model_loaded = False
        self._model_lock = threading.Lock()

        print(f"SentimentAnalyzer initialized with lazy {self.model_type} model loading")

    # =================================================
    # LOAD MODEL
    # =================================================
    def _load_model(self):

        if self.model_type == "huggingface":

            self._load_huggingface_model()

        elif self.model_type == "custom":

            self._load_custom_model()

        else:
            raise ValueError(
                f"Unsupported model: {self.model_type}"
            )

        self._model_loaded = True

    def _ensure_model_loaded(self):
        if self._model_loaded:
            return

        with self._model_lock:
            if not self._model_loaded:
                self._load_model()

    # =================================================
    # HUGGINGFACE MODEL
    # =================================================
    def _load_huggingface_model(self):

        print("Using HuggingFace model")

        self.pipeline = pipeline(
            "sentiment-analysis",
            model="wonrax/phobert-base-vietnamese-sentiment",
            tokenizer="wonrax/phobert-base-vietnamese-sentiment",
            device=0 if torch.cuda.is_available() else -1
        )

    # =================================================
    # CUSTOM MODEL
    # =================================================
    def _load_custom_model(self):

        print("Using custom PhoBERT model")

        base_dir = Path(__file__).resolve().parent


        model_path = (
            base_dir.parent.parent
            / "best_phobert_model"
        )

        model_path = str(model_path)
        print(model_path)
        print(os.path.exists(model_path))
        print(os.listdir(model_path))

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                model_path, local_files_only=True
            )
        )

        self.model = HybridPhoBERTClassifier()

        self.model.load_state_dict(
            torch.load(
                os.path.join(
                    model_path,
                    "phobert_sentiment.pth"
                ),
                map_location=self.device
            ),
            strict=False    
        )

        self.model.to(self.device)

        self.model.eval()

    # =================================================
    # SINGLE TEXT
    # =================================================
    def analyze_text(
        self,
        text: str
    ) -> Dict[str, Any]:

        self._ensure_model_loaded()

        processed = preprocess_text(text)

        # =============================================
        # HUGGINGFACE
        # =============================================
        if self.model_type == "huggingface":

            result = self.pipeline(processed)[0]

            return {
                "label": LABEL_MAPPING.get(
                    result["label"],
                    "ERROR"
                ),
                "confidence": float(result["score"]),
                "text": text
            }

        # =============================================
        # CUSTOM MODEL
        # =============================================
        encoding = self.tokenizer(
            processed,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )

        input_ids = encoding["input_ids"].to(
            self.device
        )

        attention_mask = encoding[
            "attention_mask"
        ].to(self.device)

        with torch.no_grad():

            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

            probs = torch.softmax(
                outputs.logits,
                dim=1
            )

            confidence, pred_id = torch.max(
                probs,
                dim=1
            )

        return {
            "label": ID2LABEL[pred_id.item()],
            "confidence": float(confidence.item()),
            "text": text
        }

    # =================================================
    # BATCH
    # =================================================
    def analyze_batch(
        self,
        texts: List[str]
    ):

        return [
            self.analyze_text(text)
            for text in texts
        ]

    # =================================================
    # KEYWORDS
    # =================================================
    def extract_keywords(
        self,
        texts: List[str],
        top_n: int = 10
    ):

        all_words = []

        stop_words = {
            'là', 'và', 'của',
            'có', 'được', 'cho'
        }

        for text in texts:

            words = text.lower().split()

            words = [
                word for word in words
                if word not in stop_words
                and len(word) > 1
            ]

            all_words.extend(words)

        word_counts = Counter(all_words)

        return [
            {
                "word": word,
                "count": count
            }
            for word, count
            in word_counts.most_common(top_n)
        ]
    

# this thing only for development.
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
    print("Hell Nah")
    sentiment_analyzer = SentimentAnalyzer()
