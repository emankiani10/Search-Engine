"""
preprocessing.py — Text Preprocessing Module
=============================================
Handles all text cleaning and normalization for the TF-IDF Search Engine.

Steps performed:
    1. Lowercase conversion
    2. Punctuation removal
    3. Tokenization
    4. Stopword removal
    5. Lemmatization (preferred over stemming for better word forms)
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ── Download required NLTK resources (only once) ────────────────────────────
def download_nltk_resources():
    """Download all required NLTK data packages silently."""
    resources = [
        ("tokenizers/punkt",        "punkt"),
        ("tokenizers/punkt_tab",    "punkt_tab"),
        ("corpora/stopwords",       "stopwords"),
        ("corpora/wordnet",         "wordnet"),
        ("corpora/omw-1.4",         "omw-1.4"),
    ]
    for path, pkg in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)

download_nltk_resources()

# ── Module-level singletons (created once, reused) ──────────────────────────
_LEMMATIZER   = WordNetLemmatizer()
_STOP_WORDS   = set(stopwords.words("english"))
_PUNCT_TABLE  = str.maketrans("", "", string.punctuation)


# ── Public API ───────────────────────────────────────────────────────────────
def preprocess_text(text: str) -> str:
    """
    Full preprocessing pipeline for a single document or query string.

    Parameters
    ----------
    text : str
        Raw input text.

    Returns
    -------
    str
        Space-joined string of cleaned, lemmatized tokens.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove punctuation
    text = text.translate(_PUNCT_TABLE)

    # 3. Remove extra whitespace / newlines
    text = re.sub(r"\s+", " ", text).strip()

    # 4. Tokenize
    tokens = word_tokenize(text)

    # 5. Remove stopwords and non-alphabetic tokens
    tokens = [t for t in tokens if t.isalpha() and t not in _STOP_WORDS]

    # 6. Lemmatize
    tokens = [_LEMMATIZER.lemmatize(t) for t in tokens]

    return " ".join(tokens)


def preprocess_corpus(texts) -> list:
    """
    Apply preprocess_text() to every document in a list/Series.

    Parameters
    ----------
    texts : list or pd.Series
        Collection of raw document strings.

    Returns
    -------
    list of str
        Preprocessed documents in the same order.
    """
    return [preprocess_text(str(doc)) for doc in texts]
