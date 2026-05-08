# 🔍 Noor Search Engine

A university-level **NLP / Information Retrieval** project that implements a
full-featured search engine over the BBC News dataset using TF-IDF, BM25, query
expansion, and spell correction — with a clean Streamlit UI.

---

## 📁 Project Structure

```
search_engine/
│
├── data/
│   └── bbc_news.csv          ← your dataset goes here
│
├── app.py                    ← Streamlit UI
├── preprocessing.py          ← text cleaning pipeline
├── search_engine.py          ← TF-IDF, BM25, expansion, correction
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **TF-IDF Ranking** | Cosine similarity on TF-IDF vectors (sklearn) |
| **BM25 Ranking** | Probabilistic ranking with length normalisation |
| **Spell Correction** | pyspellchecker fixes noisy queries |
| **Query Expansion** | WordNet synonyms increase recall |
| **Streamlit UI** | Responsive, professional search interface |
| **Expandable Previews** | Full article available in-place |
| **Category Labels** | Colour-coded chips per news category |

---

## 🛠️ Tech Stack

- **Python 3.11**
- **pandas** — CSV loading and DataFrame operations
- **scikit-learn** — TF-IDF vectorisation, cosine similarity
- **NLTK** — tokenisation, stopword removal, WordNet synonyms, lemmatisation
- **rank-bm25** — BM25Okapi implementation
- **pyspellchecker** — spell correction
- **Streamlit** — web UI

---

## 📊 Dataset

BBC News CSV with columns:

| Column | Description |
|--------|-------------|
| `category` | News category (sport, business, tech, politics, entertainment) |
| `filename` | Source file name |
| `title` | Article headline |
| `content` | Full article text (primary search field) |

---

## 📐 Information Retrieval Concepts

### What is Information Retrieval?
IR is the science of finding relevant information from large unstructured
collections based on user queries. Classic examples: Google Search, library
catalogues, and enterprise document search.

---

### TF-IDF

**TF (Term Frequency)**
```
TF(t, d) = (number of times t appears in d) / (total terms in d)
```
Measures how often a term occurs in a specific document.

**IDF (Inverse Document Frequency)**
```
IDF(t) = log( N / (1 + df_t) )
```
Where:
- `N`     = total number of documents
- `df_t`  = number of documents containing term t

Rare terms across the corpus get a high IDF, common terms get a low IDF.

**TF-IDF**
```
TF-IDF(t, d) = TF(t, d) × IDF(t)
```
A high score means the term is frequent in this document but rare globally —
exactly what makes a term characteristic.

---

### Cosine Similarity

After converting query and documents to TF-IDF vectors:
```
sim(q, d) = (q · d) / (||q|| × ||d||)
```
- Range: 0 (no overlap) → 1 (identical direction)
- Length-normalised: a long and a short doc with the same proportions score equally

---

### BM25

```
BM25(q, d) = Σ_t IDF(t) × [tf(t,d) × (k1+1)] / [tf(t,d) + k1 × (1−b + b×|d|/avgdl)]
```

Parameters:
- `k1 = 1.5` — term-frequency saturation (diminishing returns after repeated occurrences)
- `b  = 0.75` — document-length normalisation strength
- `avgdl`     — average document length in the corpus

**Why BM25 > TF-IDF:**
1. TF-IDF grows linearly with TF; BM25 saturates (a word appearing 100× is not 100× more relevant than appearing once).
2. BM25 penalises very long documents that contain a term simply due to length.

---

### Query Expansion (WordNet)

```python
car → automobile, vehicle, motorcar
```

- Uses NLTK's WordNet synsets to find semantically related words.
- Appended to the query before TF-IDF vectorisation.
- Improves **recall**: relevant articles that use synonyms are now retrieved.

---

### Spell Correction (pyspellchecker)

```
machien learnng → machine learning
```

- Uses word frequency dictionaries to find the most likely correction.
- Applied **before** any other processing.
- Improves **precision**: zero-match queries caused by typos are rescued.

---

### Search Pipeline

```
User Query
    │
    ▼
[1] Spell Correction          ← fix typos
    │
    ▼
[2] Query Expansion           ← add synonyms
    │
    ▼
[3] Preprocessing             ← lowercase → remove punctuation →
    │                            remove stopwords → lemmatise
    ▼
[4] Vectorisation             ← TF-IDF transform OR BM25 tokenise
    │
    ▼
[5] Scoring                   ← cosine similarity OR BM25 scores
    │
    ▼
[6] Ranking                   ← argsort descending
    │
    ▼
[7] Top-K Results             ← title, category, score, snippet
```

---

### Data Flow Diagram

```
  ┌─────────────────────────────────────────┐
  │              CSV Dataset                │
  │  category | title | content            │
  └──────────────────┬──────────────────────┘
                     │ pandas.read_csv()
                     ▼
  ┌─────────────────────────────────────────┐
  │           Preprocessing                 │
  │  lowercase → punct removal → stopwords  │
  │  → tokenise → lemmatise                │
  └──────────────────┬──────────────────────┘
                     │
           ┌─────────┴──────────┐
           ▼                    ▼
  ┌─────────────────┐  ┌─────────────────────┐
  │  TF-IDF Matrix  │  │   BM25 Index         │
  │  (sklearn)      │  │   (rank_bm25)        │
  └────────┬────────┘  └──────────┬───────────┘
           │                      │
           └──────────┬───────────┘
                      │
  ┌───────────────────▼──────────────────────┐
  │              Query Processing             │
  │  spell correct → expand → preprocess     │
  └───────────────────┬──────────────────────┘
                      │
  ┌───────────────────▼──────────────────────┐
  │              Ranking                      │
  │  cosine similarity OR BM25 score         │
  └───────────────────┬──────────────────────┘
                      │
  ┌───────────────────▼──────────────────────┐
  │          Top-K Results Display            │
  │  title | category | score | snippet      │
  └──────────────────────────────────────────┘
```

---

### Algorithms

**TF-IDF Search Algorithm**
```
1. Load CSV with pandas
2. For each document d in corpus:
   a. Preprocess(d) → cleaned string
3. Fit TfidfVectorizer on preprocessed corpus → tfidf_matrix
4. For query q:
   a. SpellCorrect(q) → q'
   b. ExpandQuery(q') → q''
   c. Preprocess(q'') → q_clean
   d. Transform q_clean → query_vector
   e. scores = cosine_similarity(query_vector, tfidf_matrix)
   f. Rank documents by scores descending
   g. Return top-K documents
```

**BM25 Algorithm**
```
1. Tokenise all preprocessed documents → token lists
2. BM25Okapi(token_lists) builds the index
3. For query q:
   a. SpellCorrect(q) → q'
   b. ExpandQuery(q') → q''
   c. Preprocess(q'') → q_clean
   d. tokens = q_clean.split()
   e. scores = bm25.get_scores(tokens)
   f. Normalise scores to [0,1]
   g. Rank descending → return top-K
```

---

## ⚡ Advantages

- Handles noisy queries via spell correction
- Improves recall via synonym expansion
- Supports two ranking algorithms (comparison ready)
- Fully modular — each concern is in its own file
- Cached index — rebuilds only once per session

## ⚠️ Limitations

- TF-IDF is bag-of-words — ignores word order and context
- WordNet expansion can introduce drift (wrong senses)
- BM25 and TF-IDF are both keyword-based; semantic search (BERT) would be stronger
- pyspellchecker is dictionary-based; rare technical terms may be mis-corrected

## 🔮 Future Improvements

- Semantic search with sentence-transformers (SBERT)
- Query auto-suggestions / autocomplete
- Filter by category before ranking
- Named entity highlighting in snippets
- Persistent index (save/load with joblib)
- REST API with FastAPI for headless access

---

## 🏗️ Installation & Running

### Option A — Local (VSCode)

```bash
# 1. Clone / open project
cd noor_search_engine

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place dataset
mkdir -p data
cp /path/to/bbc_news.csv data/

# 5. Run
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

### Option B — Docker

```bash
# 1. Place dataset in data/ folder
mkdir -p data && cp /path/to/bbc_news.csv data/

# 2. Build & run
docker compose up --build

# OR without compose:
docker build -t noor-search .
docker run -p 8501:8501 -v $(pwd)/data:/app/data noor-search
```

Open `http://localhost:8501`.

---

### Option C — GitHub Actions CI (optional)

Push to GitHub; add `.github/workflows/ci.yml` that runs:
```yaml
- pip install -r requirements.txt
- python -c "from search_engine import SearchEngine; print('OK')"
```

---

## 👩‍💻 Author

**Noor** — University NLP / LP Assignment  
Stack: Python · scikit-learn · NLTK · rank-bm25 · Streamlit · Docker
