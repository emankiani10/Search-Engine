"""
search_engine.py — Core Search Engine Module
=============================================
Implements:
    • TF-IDF vectorisation + Cosine Similarity ranking  (sklearn)
    • BM25 ranking                                       (rank_bm25)
    • Query expansion via WordNet synonyms               (NLTK)
    • Spell correction                                   (pyspellchecker)

Information Retrieval Concepts
--------------------------------
TF-IDF (Term Frequency–Inverse Document Frequency):
    Weighs how important a word is to a document relative to the corpus.
    - TF  = (occurrences of term t in doc d) / (total terms in doc d)
    - IDF = log(N / (1 + df_t))   where N = total docs, df_t = docs containing t
    - TF-IDF = TF × IDF

Cosine Similarity:
    Measures the angle between the query vector and each document vector.
    sim(q, d) = (q · d) / (||q|| × ||d||)
    Range: [0, 1] — 1 means identical direction (most relevant).

BM25 (Best Match 25):
    Probabilistic ranking that adds document-length normalisation and
    term-frequency saturation, outperforming TF-IDF on longer docs.
    BM25(q,d) = Σ IDF(t) × [tf(t,d)(k1+1)] / [tf(t,d) + k1(1−b+b·|d|/avgdl)]
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from spellchecker import SpellChecker
import nltk
from nltk.corpus import wordnet

from preprocessing import preprocess_text, preprocess_corpus, download_nltk_resources

download_nltk_resources()

# ── Spell checker singleton ──────────────────────────────────────────────────
_SPELL = SpellChecker()


# ════════════════════════════════════════════════════════════════════════════
#  Query Helpers
# ════════════════════════════════════════════════════════════════════════════

def correct_spelling(query: str) -> tuple[str, bool]:
    """
    Correct misspelled words in *query* using pyspellchecker.

    Returns
    -------
    (corrected_query, was_corrected) : tuple
        corrected_query : str  — query with fixed spellings
        was_corrected   : bool — True if any word was changed
    """
    words     = query.split()
    corrected = []
    changed   = False

    for word in words:
        fixed = _SPELL.correction(word)
        if fixed and fixed != word.lower():
            corrected.append(fixed)
            changed = True
        else:
            corrected.append(word)

    return " ".join(corrected), changed


def expand_query(query: str) -> tuple[str, list]:
    """
    Expand *query* with WordNet synonyms to improve recall.

    Strategy:
        For each content word (after preprocessing) look up synsets in WordNet.
        Add lemma names that are single words and different from the original.
        Limit expansion to 2 synonyms per term to avoid query drift.

    Returns
    -------
    (expanded_query, synonyms_added) : tuple
        expanded_query : str  — original + synonym terms
        synonyms_added : list — list of (original_term, [synonyms]) pairs
    """
    tokens         = query.lower().split()
    extra_terms    = []
    synonyms_log   = []

    for token in tokens:
        syns = set()
        for synset in wordnet.synsets(token):
            for lemma in synset.lemmas():
                name = lemma.name().replace("_", " ")
                if name != token and name.isalpha():
                    syns.add(name)
        syns = list(syns)[:2]          # limit to 2 synonyms per word
        if syns:
            extra_terms.extend(syns)
            synonyms_log.append((token, syns))

    expanded = query + " " + " ".join(extra_terms) if extra_terms else query
    return expanded.strip(), synonyms_log


# ════════════════════════════════════════════════════════════════════════════
#  SearchEngine Class
# ════════════════════════════════════════════════════════════════════════════

class SearchEngine:
    """
    Unified search engine supporting TF-IDF and BM25 ranking.

    Usage
    -----
    engine = SearchEngine()
    engine.build_index(df)          # df must have: title, category, content
    results = engine.search("query", method="tfidf", top_k=5)
    """

    def __init__(self):
        self.df              = None          # original DataFrame
        self.processed_docs  = []            # preprocessed content strings
        self.tokenized_docs  = []            # tokenized lists (for BM25)

        # TF-IDF artefacts
        self.vectorizer      = TfidfVectorizer(
            max_features=50_000,
            ngram_range=(1, 2),              # unigrams + bigrams
            sublinear_tf=True,               # apply 1+log(tf) smoothing
        )
        self.tfidf_matrix    = None

        # BM25 artefact
        self.bm25            = None

        self.is_built        = False

    # ── Index construction ───────────────────────────────────────────────────

    def build_index(self, df: pd.DataFrame) -> None:
        """
        Pre-process corpus and build both TF-IDF and BM25 indices.

        Parameters
        ----------
        df : pd.DataFrame
            Must contain columns: title, category, content
        """
        self.df = df.reset_index(drop=True)

        # 1. Preprocess all documents
        self.processed_docs = preprocess_corpus(self.df["content"].tolist())

        # 2. Build TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_docs)

        # 3. Build BM25 index (needs tokenised lists)
        self.tokenized_docs = [doc.split() for doc in self.processed_docs]
        self.bm25           = BM25Okapi(self.tokenized_docs)

        self.is_built = True

    # ── Search ───────────────────────────────────────────────────────────────

    def search(
        self,
        query:          str,
        method:         str  = "tfidf",
        top_k:          int  = 5,
        use_expansion:  bool = True,
        use_correction: bool = True,
    ) -> dict:
        """
        Run a search query against the indexed corpus.

        Parameters
        ----------
        query          : str  — raw user query
        method         : str  — "tfidf" or "bm25"
        top_k          : int  — number of results to return
        use_expansion  : bool — apply WordNet query expansion
        use_correction : bool — apply spell correction

        Returns
        -------
        dict with keys:
            original_query   : str
            corrected_query  : str
            was_corrected    : bool
            expanded_query   : str
            synonyms_added   : list
            results          : list of result dicts
            method           : str
        """
        if not self.is_built:
            raise RuntimeError("Index not built. Call build_index() first.")

        original_query  = query
        was_corrected   = False
        corrected_query = query
        synonyms_added  = []

        # ── Step 1: Spell correction ─────────────────────────────────────
        if use_correction:
            corrected_query, was_corrected = correct_spelling(query)
            query = corrected_query

        # ── Step 2: Query expansion ──────────────────────────────────────
        expanded_query = query
        if use_expansion:
            expanded_query, synonyms_added = expand_query(query)

        # ── Step 3: Preprocess query ─────────────────────────────────────
        processed_query = preprocess_text(expanded_query)

        # ── Step 4: Rank ─────────────────────────────────────────────────
        if method == "tfidf":
            scores = self._tfidf_score(processed_query)
        else:
            scores = self._bm25_score(processed_query)

        # ── Step 5: Retrieve top-k results ───────────────────────────────
        top_indices = np.argsort(scores)[::-1][:top_k]
        results     = []

        for rank, idx in enumerate(top_indices, start=1):
            score = float(scores[idx])
            if score <= 0:
                break
            row = self.df.iloc[idx]
            results.append({
                "rank":     rank,
                "title":    row.get("title", "Untitled"),
                "category": row.get("category", "Unknown"),
                "score":    round(score, 4),
                "snippet":  self._snippet(str(row.get("content", "")), corrected_query),
                "content":  str(row.get("content", "")),
            })

        return {
            "original_query":  original_query,
            "corrected_query": corrected_query,
            "was_corrected":   was_corrected,
            "expanded_query":  expanded_query,
            "synonyms_added":  synonyms_added,
            "results":         results,
            "method":          method.upper(),
        }

    # ── Scoring helpers ──────────────────────────────────────────────────────

    def _tfidf_score(self, processed_query: str) -> np.ndarray:
        """Compute cosine similarity between query vector and all docs."""
        query_vec = self.vectorizer.transform([processed_query])
        sims      = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        return sims

    def _bm25_score(self, processed_query: str) -> np.ndarray:
        """Compute BM25 scores for the processed query tokens."""
        tokens = processed_query.split()
        scores = np.array(self.bm25.get_scores(tokens))
        # Normalise to [0, 1] for comparability with TF-IDF
        max_s  = scores.max()
        if max_s > 0:
            scores = scores / max_s
        return scores

    # ── Snippet generator ────────────────────────────────────────────────────

    @staticmethod
    def _snippet(content: str, query: str, window: int = 300) -> str:
        """
        Return a ~300-char excerpt from *content* nearest to query terms.
        Falls back to the first 300 characters if no match found.
        """
        lower_content = content.lower()
        best_pos      = 0

        for word in query.lower().split():
            pos = lower_content.find(word)
            if pos != -1:
                best_pos = pos
                break

        start   = max(0, best_pos - 50)
        snippet = content[start : start + window]
        if start > 0:
            snippet = "…" + snippet
        if start + window < len(content):
            snippet += "…"
        return snippet
