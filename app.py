"""
app.py — Streamlit UI for QueryLens Search Engine
=================================================
Run with:  streamlit run app.py
"""

import os
import time
import pandas as pd
import streamlit as st

from search_engine import SearchEngine

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QueryLens Search Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap');

:root {
    --bg:        #fafaf9;
    --surface:   #ffffff;
    --border:    #e7e5e4;
    --border-2:  #d6d3d1;
    --ink:       #1c1917;
    --ink-2:     #44403c;
    --muted:     #78716c;
    --accent:    #0f766e;
    --accent-2:  #115e59;
    --accent-bg: #f0fdfa;
    --warn:      #b45309;
    --warn-bg:   #fffbeb;
    --info:      #1d4ed8;
    --info-bg:   #eff6ff;
}

html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}
[data-testid="stAppViewContainer"] { background: var(--bg); }

/* Hide Streamlit chrome we don't need (keep header so sidebar toggle stays) */
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 1rem; }
.block-container { padding-top: 2rem; max-width: 1100px; }

/* ── Header ───────────────────────────────────────────────────────────────── */
.header-block {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.4rem;
    margin-bottom: 2rem;
}
.header-block .eyebrow {
    color: var(--accent);
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.header-block h1 {
    font-size: 2.1rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    color: var(--ink);
    margin: 0 0 0.35rem 0;
    line-height: 1.15;
}
.header-block .subtitle {
    color: var(--ink-2);
    font-size: 0.98rem;
    margin: 0;
}

/* ── Stat row ─────────────────────────────────────────────────────────────── */
.stat-row { display: flex; gap: 1rem; margin-bottom: 1.6rem; flex-wrap: wrap; }
.stat-card {
    flex: 1;
    min-width: 180px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.95rem 1.1rem;
}
.stat-card .label {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.stat-card .value {
    color: var(--ink);
    font-size: 1.55rem;
    font-weight: 700;
    margin-top: 0.2rem;
    letter-spacing: -0.02em;
}

/* ── Search input ─────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: 10px !important;
    padding: 0.9rem 1rem !important;
    font-size: 1rem !important;
    color: var(--ink) !important;
    box-shadow: 0 1px 2px rgba(28,25,23,0.04);
    transition: border-color 0.15s, box-shadow 0.15s;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(15,118,110,0.12) !important;
    outline: none !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: 1px solid var(--accent) !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    transition: background 0.15s;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: var(--accent-2) !important;
    border-color: var(--accent-2) !important;
}
.stButton > button p { white-space: nowrap !important; overflow: visible !important; }

/* ── Notice boxes ─────────────────────────────────────────────────────────── */
.notice {
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem 1.05rem;
    margin-bottom: 0.7rem;
    font-size: 0.92rem;
    line-height: 1.55;
    color: var(--ink-2);
    background: var(--surface);
}
.notice strong { color: var(--ink); font-weight: 600; }
.notice .tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 0.55rem;
    vertical-align: 1px;
}
.notice.correction .tag { background: var(--warn-bg);   color: var(--warn);   border: 1px solid #fde68a; }
.notice.expansion  .tag { background: var(--accent-bg); color: var(--accent); border: 1px solid #99f6e4; }
.notice.method     .tag { background: var(--info-bg);   color: var(--info);   border: 1px solid #bfdbfe; }

/* ── Result card ──────────────────────────────────────────────────────────── */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 0.9rem;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.result-card:hover {
    border-color: var(--border-2);
    box-shadow: 0 2px 8px rgba(28,25,23,0.05);
}
.result-card .meta {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 0.45rem;
    flex-wrap: wrap;
}
.result-card .rank {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    font-weight: 500;
}
.result-card h3 {
    color: var(--ink);
    font-size: 1.08rem;
    font-weight: 600;
    line-height: 1.35;
    margin: 0 0 0.45rem 0;
    letter-spacing: -0.01em;
}
.result-card .snippet {
    color: var(--ink-2);
    font-size: 0.94rem;
    line-height: 1.6;
}
.result-card .snippet mark {
    background: #fef08a;
    color: var(--ink);
    padding: 0 2px;
    border-radius: 2px;
}

/* ── Category chip ────────────────────────────────────────────────────────── */
.cat-chip {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border: 1px solid transparent;
}
.cat-sport         { background:#e0f2fe; color:#075985; border-color:#bae6fd; }
.cat-business      { background:#dcfce7; color:#14532d; border-color:#bbf7d0; }
.cat-tech          { background:#fef3c7; color:#78350f; border-color:#fde68a; }
.cat-politics      { background:#fce7f3; color:#831843; border-color:#fbcfe8; }
.cat-entertainment { background:#ede9fe; color:#4c1d95; border-color:#ddd6fe; }
.cat-default       { background:#f5f5f4; color:#44403c; border-color:#e7e5e4; }

/* ── Score badge ──────────────────────────────────────────────────────────── */
.score-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 500;
    color: var(--muted);
    margin-left: auto;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
.sidebar-section {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.1rem 0 0.4rem 0;
}
.sidebar-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.3rem;
    letter-spacing: -0.01em;
}
.sidebar-sub {
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 1rem;
}
[data-testid="stSidebar"] hr { margin: 0.4rem 0 !important; border-color: var(--border); }

/* ── Suggestion chips ─────────────────────────────────────────────────────── */
.suggestion-row { color: var(--muted); font-size: 0.85rem; margin: 0.6rem 0 1.4rem 0; }
.suggestion-row .label { font-weight: 500; margin-right: 0.5rem; }

/* ── Expander ─────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader { font-weight: 500 !important; color: var(--ink-2) !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  Index loader (cached once per session)
# ════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_engine(csv_path: str):
    df = pd.read_csv(csv_path)
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
    st.markdown('<div class="sidebar-title">QueryLens</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-sub">Information retrieval over the BBC News corpus.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">Dataset</div>', unsafe_allow_html=True)
    csv_path = st.text_input(
        "CSV file path",
        value="data/bbc_news.csv",
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section">Ranking</div>', unsafe_allow_html=True)
    ranking_method = st.radio(
        "Ranking method",
        options=["TF-IDF", "BM25"],
        index=0,
        label_visibility="collapsed",
    )

    top_k = st.slider("Number of results", min_value=1, max_value=20, value=5)

    st.markdown('<div class="sidebar-section">Query options</div>', unsafe_allow_html=True)
    use_correction = st.checkbox("Spell correction",  value=True)
    use_expansion  = st.checkbox("Query expansion",   value=True)

# ════════════════════════════════════════════════════════════════════════════
#  Header
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-block">
  <div class="eyebrow">QueryLens · NUTECH NLP Project</div>
  <h1>Search the BBC News corpus</h1>
  <p class="subtitle">TF-IDF and BM25 ranking with WordNet query expansion and spell correction.</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  Load engine
# ════════════════════════════════════════════════════════════════════════════

if not os.path.exists(csv_path):
    st.error(
        f"Dataset not found at `{csv_path}`. "
        "Place `bbc_news.csv` in the `data/` folder, or update the path in the sidebar."
    )
    st.stop()

with st.spinner("Building search index — first load only…"):
    try:
        engine, df = load_engine(csv_path)
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

# Stat row
all_categories = sorted(df["category"].dropna().astype(str).unique().tolist())
st.markdown(f"""
<div class="stat-row">
  <div class="stat-card"><div class="label">Articles</div><div class="value">{len(df):,}</div></div>
  <div class="stat-card"><div class="label">Categories</div><div class="value">{len(all_categories)}</div></div>
  <div class="stat-card"><div class="label">Ranking</div><div class="value">{ranking_method}</div></div>
</div>
""", unsafe_allow_html=True)

# Sidebar — categories filter (after load so we know the values)
with st.sidebar:
    st.markdown('<div class="sidebar-section">Filter by category</div>', unsafe_allow_html=True)
    selected_categories = st.multiselect(
        "Categories",
        options=all_categories,
        default=[],
        label_visibility="collapsed",
        placeholder="All categories",
    )

# ════════════════════════════════════════════════════════════════════════════
#  Search bar
# ════════════════════════════════════════════════════════════════════════════

# Suggestion buttons feed the search input via on_click callbacks.
# We can't write to a widget's key after the widget is instantiated on the same
# run, so we use on_click handlers — those execute *before* the rerun, so the
# text_input picks up the new value cleanly on the next render.
SUGGESTIONS = ["economy", "football", "election", "technology"]

if "query_input" not in st.session_state:
    st.session_state["query_input"] = ""


def _set_query(value: str) -> None:
    st.session_state["query_input"] = value


query_col, btn_col = st.columns([6, 1])
with query_col:
    query = st.text_input(
        "Search",
        key="query_input",
        placeholder='Try "machine learning economy" or "footbal champion"',
        label_visibility="collapsed",
    )
with btn_col:
    search_clicked = st.button("Search", use_container_width=True, type="primary")

# Suggestion chips — fit content width so words don't wrap
sugg_cols = st.columns([0.6, 1.2, 1.2, 1.2, 1.2, 4])
sugg_cols[0].markdown(
    '<div class="suggestion-row"><span class="label">Try:</span></div>',
    unsafe_allow_html=True,
)
for i, s in enumerate(SUGGESTIONS):
    sugg_cols[i + 1].button(
        s,
        key=f"sugg_{i}",
        use_container_width=True,
        on_click=_set_query,
        args=(s,),
    )

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


run_search = search_clicked or (query and st.session_state.get("_last_query") != query)

if run_search and query.strip():
    st.session_state["_last_query"] = query
    t0 = time.time()
    with st.spinner("Searching…"):
        response = engine.search(
            query=query,
            method=ranking_method.lower(),
            top_k=top_k,
            use_expansion=use_expansion,
            use_correction=use_correction,
            categories=selected_categories or None,
        )
    elapsed = time.time() - t0

    if response["was_corrected"]:
        st.markdown(
            f'<div class="notice correction"><span class="tag">Spell correction</span>'
            f'<em>"{response["original_query"]}"</em> → '
            f'<strong>"{response["corrected_query"]}"</strong></div>',
            unsafe_allow_html=True,
        )

    if use_expansion and response["synonyms_added"]:
        pairs = ", ".join(
            f'<strong>{t}</strong> → {", ".join(s)}' for t, s in response["synonyms_added"]
        )
        st.markdown(
            f'<div class="notice expansion"><span class="tag">Query expansion</span>{pairs}</div>',
            unsafe_allow_html=True,
        )

    filter_note = (
        f' &nbsp;·&nbsp; filtered to: <strong>{", ".join(selected_categories)}</strong>'
        if selected_categories else ""
    )
    st.markdown(
        f'<div class="notice method"><span class="tag">{response["method"]}</span>'
        f'{elapsed:.3f}s &nbsp;·&nbsp; '
        f'<strong>{len(response["results"])}</strong> results{filter_note}</div>',
        unsafe_allow_html=True,
    )

    if not response["results"]:
        st.warning("No relevant results. Try a different query, broaden categories, or enable expansion.")
    else:
        for res in response["results"]:
            st.markdown(f"""
<div class="result-card">
  <div class="meta">
    <span class="rank">#{res['rank']:02d}</span>
    {category_chip(res['category'])}
    <span class="score-badge">score {res['score']:.4f}</span>
  </div>
  <h3>{res['title']}</h3>
  <div class="snippet">{res['snippet']}</div>
</div>
""", unsafe_allow_html=True)

            with st.expander(f"Read full article — {res['title']}"):
                st.write(res["content"])

elif search_clicked and not query.strip():
    st.warning("Please enter a search query.")

# ════════════════════════════════════════════════════════════════════════════
#  Concepts footer
# ════════════════════════════════════════════════════════════════════════════

st.markdown("---")
with st.expander("Information retrieval — concepts and formulas"):
    st.markdown("""
**TF-IDF** weighs how distinctive a term is to a document:

```
tf(t,d)  = count(t in d) / len(d)
idf(t)   = log(N / (1 + df_t))
tfidf    = tf × idf
```

**Cosine similarity** measures the angle between query and document vectors:

```
sim(q, d) = (q · d) / (||q|| × ||d||)
```

**BM25** adds length normalisation and term-frequency saturation:

```
BM25(q,d) = Σ IDF(t) × [tf(t,d)(k1+1)] / [tf(t,d) + k1(1 − b + b·|d|/avgdl)]
```

with `k1 = 1.5`, `b = 0.75`. Better than raw TF-IDF on long, varied documents.

**Query expansion** uses WordNet synonyms to improve recall — searching for *car*
also matches *automobile* or *vehicle*. **Spell correction** fixes noisy queries
like *machien lerning* before vectorisation, dramatically improving precision.
**Stop-word removal** and **lemmatisation** strip noise and collapse inflected
forms (*running → run*) so variants share an index entry.
""")
