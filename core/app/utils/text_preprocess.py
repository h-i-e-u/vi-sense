import re

from underthesea import word_tokenize


def preprocess_text(text: str) -> str:

    text = re.sub(r'\s+', ' ', text.strip())

    text = re.sub(r'[.!?]{2,}', '.', text)

    text = text.lower()

    text = word_tokenize(
        text,
        format="text"
    )

    return text