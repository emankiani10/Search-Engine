"""
app.py — Streamlit UI for Noor Search Engine
=============================================
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import time
import os

from search_engine import SearchEngine

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Noor Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global font & background ── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Header ── */
.main-header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
}
.main-header h1 { font-size: 2.4rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.main-header p  { opacity: 0.75; margin: 0.4rem 0 0; font-size: 1rem; }

/* ── Result card ── */
.result-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2c5364;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s;
}
.result-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

/* ── Score badge ── */
.score-badge {
    display: inline-block;
    background: #2c5364;
    color: white;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.8rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    margin-left: 8px;
}

/* ── Category chip ── */
.cat-chip {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-right: 6px;
}
.cat-sport     { background:#dbeafe; color:#1d4ed8; }
.cat-business  { background:#dcfce7; color:#166534; }
.cat-tech      { background:#fef3c7; color:#92400e; }
.cat-politics  { background:#fce7f3; color:#9d174d; }
.cat-entertainment { background:#ede9fe; color:#5b21b6; }
.cat-default   { background:#f1f5f9; color:#334155; }

/* ── Info boxes ── */
.info-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    margin-bottom: 0.8rem;
    line-height: 1.6;
}
.correction-box { border-left: 4px solid #f59e0b; background: #fffbeb; }
.expansion-box  { border-left: 4px solid #10b981; background: #ecfdf5; }
.method-box     { border-left: 4px solid #6366f1; background: #eef2ff; }

/* ── Snippet ── */
.snippet { color: #64748b; font-size: 0.9rem; line-height: 1.55; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  Session-State: build index once per session
# ════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_engine(csv_path: str) -> tuple:
    """Load CSV and build search index (cached across reruns)."""
    df = pd.read_csv(csv_path)
    # Normalise column names
    df.columns = [c.strip().lower() for c in df.columns]
    required = {"title", "category", "content"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")

    engine = SearchEngine()
    engine.build_index(df)
    return engine, df


# ════════════════════════════════════════════════════════════════════════════
#  Sidebar
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Settings")

    csv_path = st.text_input(
        "📂 CSV file path",
        value="data/bbc_news.csv",
        help="Relative or absolute path to your BBC News CSV file",
    )

    st.markdown("---")
    ranking_method = st.radio(
        "🏆 Ranking Method",
        options=["TF-IDF", "BM25"],
        index=0,
        help="TF-IDF uses cosine similarity; BM25 adds length normalisation.",
    )

    top_k = st.slider("📄 Number of Results", min_value=1, max_value=20, value=5)

    st.markdown("---")
    use_correction = st.checkbox("✏️ Spell Correction",  value=True)
    use_expansion  = st.checkbox("🔗 Query Expansion",   value=True)

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown(
        "**Noor Search Engine** — A university-level NLP/IR project "
        "implementing TF-IDF, BM25, spell correction, and query expansion "
        "on the BBC News dataset."
    )

# ════════════════════════════════════════════════════════════════════════════
#  Header
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
  <h1>🔍 Noor Search Engine</h1>
  <p>TF-IDF · BM25 · Query Expansion · Spell Correction · BBC News Corpus</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  Load Engine
# ════════════════════════════════════════════════════════════════════════════

if not os.path.exists(csv_path):
    st.error(
        f"❌ Dataset not found at **`{csv_path}`**.\n\n"
        "Place your `bbc_news.csv` in the `data/` folder, or update the path in the sidebar."
    )
    st.stop()

with st.spinner("⚙️ Building search index… (first load only)"):
    try:
        engine, df = load_engine(csv_path)
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

# Dataset quick stats
col1, col2, col3 = st.columns(3)
col1.metric("📰 Total Articles", f"{len(df):,}")
col2.metric("🗂️ Categories",     df["category"].nunique())
col3.metric("🏆 Ranking",        ranking_method)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
#  Search Box
# ════════════════════════════════════════════════════════════════════════════

query_col, btn_col = st.columns([5, 1])
with query_col:
    query = st.text_input(
        "Search",
        placeholder='e.g. "machine learning economy" or "footbal champion"',
        label_visibility="collapsed",
    )
with btn_col:
    search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")

# ════════════════════════════════════════════════════════════════════════════
#  Results
# ════════════════════════════════════════════════════════════════════════════

CAT_CSS = {
    "sport":         "cat-sport",
    "business":      "cat-business",
    "tech":          "cat-tech",
    "technology":    "cat-tech",
    "politics":      "cat-politics",
    "entertainment": "cat-entertainment",
}


def category_chip(category: str) -> str:
    css = CAT_CSS.get(category.lower(), "cat-default")
    return f'<span class="cat-chip {css}">{category}</span>'


if search_clicked and query.strip():
    t0 = time.time()

    with st.spinner("Searching…"):
        response = engine.search(
            query=query,
            method=ranking_method.lower(),
            top_k=top_k,
            use_expansion=use_expansion,
            use_correction=use_correction,
        )

    elapsed = time.time() - t0

    # ── Correction notice ────────────────────────────────────────────────
    if response["was_corrected"]:
        st.markdown(
            f'<div class="info-box correction-box">✏️ <strong>Spell Correction:</strong> '
            f'<em>"{response["original_query"]}"</em> → '
            f'<strong>"{response["corrected_query"]}"</strong></div>',
            unsafe_allow_html=True,
        )

    # ── Expansion notice ─────────────────────────────────────────────────
    if use_expansion and response["synonyms_added"]:
        pairs = ", ".join(
            f"{t} → [{', '.join(s)}]" for t, s in response["synonyms_added"]
        )
        st.markdown(
            f'<div class="info-box expansion-box">🔗 <strong>Query Expansion:</strong> {pairs}</div>',
            unsafe_allow_html=True,
        )

    # ── Method + timing ─────────────────────────────────────────────────
    st.markdown(
        f'<div class="info-box method-box">🏆 <strong>Ranking:</strong> {response["method"]} &nbsp;|&nbsp; '
        f'⏱ <strong>{elapsed:.3f}s</strong> &nbsp;|&nbsp; '
        f'📄 <strong>{len(response["results"])}</strong> results</div>',
        unsafe_allow_html=True,
    )

    # ── Result cards ─────────────────────────────────────────────────────
    if not response["results"]:
        st.warning("No relevant results found. Try a different query or enable query expansion.")
    else:
        for res in response["results"]:
            chip  = category_chip(res["category"])
            score = res["score"]

            st.markdown(f"""
<div class="result-card">
  <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
    <span style="font-weight:700; font-size:1.05rem;">#{res['rank']} &nbsp;{res['title']}</span>
    {chip}
    <span class="score-badge">Score: {score:.4f}</span>
  </div>
  <div class="snippet">{res['snippet']}</div>
</div>
""", unsafe_allow_html=True)

            with st.expander(f"📖 Full article — {res['title']}"):
                st.write(res["content"])

elif search_clicked and not query.strip():
    st.warning("⚠️ Please enter a search query.")

# ════════════════════════════════════════════════════════════════════════════
#  Information Retrieval Concepts Tab (footer)
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
with st.expander("📚 Information Retrieval Concepts & Formulas"):
    st.markdown("""
### What is Information Retrieval?
Information Retrieval (IR) is the science of obtaining relevant information from
large collections of unstructured data (documents, web pages, articles) based on
user queries. A search engine is the classic IR application.

---

### TF-IDF
**Term Frequency–Inverse Document Frequency** assigns a weight to each term in a
document that reflects how *distinctive* that term is:

| Component | Formula | Intuition |
|-----------|---------|-----------|
| TF  | `tf(t,d) = count(t in d) / len(d)` | How often term appears in this doc |
| IDF | `idf(t) = log(N / (1 + df_t))` | How rare the term is across all docs |
| TF-IDF | `tfidf(t,d) = tf × idf` | Combined importance weight |

---

### Cosine Similarity
Measures the angle between query vector **q** and document vector **d**:

```
sim(q, d) = (q · d) / (||q|| × ||d||)
```

Range: 0 (unrelated) → 1 (identical direction).

---

### BM25 Formula
```
BM25(q,d) = Σ IDF(t) × [tf(t,d)(k1+1)] / [tf(t,d) + k1(1 − b + b·|d|/avgdl)]
```
- **k1 = 1.5** — controls term-frequency saturation  
- **b  = 0.75** — controls document-length normalisation  
- **avgdl**     — average document length in the corpus  

BM25 penalises very long documents and saturates TF, giving better rankings than
raw TF-IDF on real-world corpora.

---

### Why Query Expansion?
WordNet synonyms increase **recall**: a search for *car* also matches documents
about *automobile* and *vehicle*, surfacing relevant articles that lack the exact
query word.

### Why Spell Correction?
Noisy queries (*machien lerning*) produce zero TF-IDF matches. Correcting to
*machine learning* before vectorisation dramatically improves **precision**.

### Why Stopword Removal?
Words like *the, is, a* appear in every document and carry no discriminative
power. Removing them reduces noise and speeds up computation.

### Why Lemmatisation?
Reduces inflected forms to their base (*running → run*, *cars → car*), ensuring
*runs* and *running* match the same index term.
""")
