import os
import re
import threading
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

import joblib
from dotenv import load_dotenv
load_dotenv()

ASPECT_KEYWORDS = {
    "CAMERA": ["camera", "chụp ảnh", "quay phim", "selfie", "ống kính", "hình ảnh", "chụp", "quay"],
    "BATTERY": ["pin", "bin", "sạc", "sac", "dung lượng", "trâu"],
    "PRICE": ["giá", "tiền", "giá thành", "chát", "đắt", "rẻ", "túi tiền", "mua"],
    "SCREEN": ["màn hình", "màn", "hiển thị", "màu sắc", "screen"],
    "PERFORMANCE": ["mượt", "lag", "đơ", "chơi game", "hiệu năng", "cấu hình", "chip", "tốc độ", "load"],
    "FEATURES": ["loa", "wifi", "wf", "sóng", "vân tay", "khu khuôn mặt", "bluetooth", "tính năng", "chức năng"],
    "DESIGN": ["thiết kế", "đẹp", "màu", "vỏ", "sang trọng", "ngoại hình", "cầm"],
    "SER&ACC": ["nhân viên", "tư vấn", "phục vụ", "giao hàng", "bảo hành", "nhiệt tình"],
    "STORAGE": ["bộ nhớ", "dung lượng", "rom", "ram", "lưu trữ", "gb"],
    "GENERAL": ["máy", "điện thoại", "sản phẩm", "ok", "tốt", "dùng", "xài"],
}


class ABSAService:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or os.getenv("ABSA_MODEL_PATH", "absa_svm_model.pkl")
        self.model = None
        self._model_loaded = False
        self._model_lock = threading.Lock()

    def _resolve_model_path(self) -> Path:
        configured_path = Path(self.model_path)
        if configured_path.is_absolute() and configured_path.exists():
            if configured_path.is_dir():
                preferred_model = configured_path / "absa_svm_model.pkl"
                if preferred_model.exists():
                    return preferred_model
                model_files = sorted(configured_path.glob("*.pkl"))
                if model_files:
                    return model_files[0]
            return configured_path

        core_dir = Path(__file__).resolve().parents[2]
        candidates = [
            Path.cwd() / configured_path,
            core_dir / configured_path,
            core_dir / "absa_model" / configured_path,
            core_dir / "absa_model",
            core_dir.parent / configured_path,
        ]

        for candidate in candidates:
            if candidate.exists():
                if candidate.is_dir():
                    preferred_model = candidate / "absa_svm_model.pkl"
                    if preferred_model.exists():
                        return preferred_model
                    model_files = sorted(candidate.glob("*.pkl"))
                    if model_files:
                        return model_files[0]
                return candidate

        searched = ", ".join(str(candidate) for candidate in candidates)
        raise FileNotFoundError(
            f"ABSA model not found. Set ABSA_MODEL_PATH or place {self.model_path}. Searched: {searched}"
        )

    def _ensure_model_loaded(self):
        if self._model_loaded:
            return

        with self._model_lock:
            if not self._model_loaded:
                self.model = joblib.load(self._resolve_model_path())
                self._model_loaded = True

    def _clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'([,.\?!\(\)\-"\'])', r" \1 ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _get_context_window(self, cleaned_text: str, aspect_name: str, window_size: int = 5) -> str:
        words = cleaned_text.split()
        keywords = ASPECT_KEYWORDS.get(aspect_name, [])

        for idx, word in enumerate(words):
            if any(keyword == word for keyword in keywords) or any(keyword in word for keyword in keywords):
                start = max(0, idx - window_size)
                end = min(len(words), idx + window_size + 1)
                return " ".join(words[start:end])

        return cleaned_text

    def analyze(self, raw_comment: str) -> List[Dict[str, str]]:
        self._ensure_model_loaded()

        if not raw_comment or not raw_comment.strip():
            return []

        cleaned_text = self._clean_text(raw_comment)
        results = []

        for aspect in ASPECT_KEYWORDS.keys():
            context_text = self._get_context_window(cleaned_text, aspect)

            if context_text != cleaned_text or aspect == "GENERAL":
                input_format = f"{context_text} [ASPECT] {aspect}"
                pred_sentiment = self.model.predict([input_format])[0]
                results.append(
                    {
                        "aspect": aspect,
                        "sentiment": str(pred_sentiment),
                        "context": context_text,
                    }
                )

        return results

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [
            {
                "index": index,
                "aspects": self.analyze(text),
            }
            for index, text in enumerate(texts)
        ]

    def summarize(self, absa_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        aspect_counts = Counter()
        sentiment_counts = Counter()
        aspect_sentiments = defaultdict(Counter)

        for item in absa_results:
            for aspect_result in item["aspects"]:
                aspect = aspect_result["aspect"]
                sentiment = aspect_result["sentiment"]
                aspect_counts[aspect] += 1
                sentiment_counts[sentiment] += 1
                aspect_sentiments[aspect][sentiment] += 1

        return {
            "total_aspect_mentions": sum(aspect_counts.values()),
            "aspect_counts": dict(aspect_counts),
            "sentiment_counts": dict(sentiment_counts),
            "aspect_sentiments": {
                aspect: dict(sentiments)
                for aspect, sentiments in aspect_sentiments.items()
            },
            "top_aspects": [
                {"aspect": aspect, "count": count}
                for aspect, count in aspect_counts.most_common(5)
            ],
        }


absa_analyzer = ABSAService()
