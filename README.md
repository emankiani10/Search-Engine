**NLP | National University of Technology**

# 🔍 QueryLens Search Engine

### Advanced Information Retrieval System for BBC News Analytics

**QueryLens** is a university-level Information Retrieval (IR) and Natural Language Processing (NLP) framework designed to provide high-precision search capabilities over structured news datasets. By integrating probabilistic ranking models like BM25 with traditional vector space models (TF-IDF), QueryLens bridges the gap between raw data and actionable insights.

---

## 📂 Project Architecture

The system is designed with a modular architecture to ensure scalability and ease of maintenance.

| Module | Component | Responsibility |
| --- | --- | --- |
| **Frontend** | `app.py` | Streamlit-based interface and session state management. |
| **Core Engine** | `search_engine.py` | Implementation of TF-IDF, BM25, and similarity scoring. |
| **NLP Pipeline** | `preprocessing.py` | Tokenization, lemmatization, and stop-word filtering. |
| **Data Layer** | `/data/` | Storage for the BBC News CSV corpus. |
| **DevOps** | `Dockerfile` | Containerization and environment reproducibility. |

---

## 🛠️ Technical Specifications

QueryLens utilizes a sophisticated pipeline to transform unstructured text into searchable mathematical vectors.

### Core Technologies

* **Linguistic Processing:** NLTK (WordNet & Lemmatizer).
* **Vectorization:** Scikit-learn (TfidfVectorizer).
* **Probabilistic Modeling:** Rank-BM25.
* **Typo Tolerance:** Pyspellchecker.
* **Interface:** Streamlit Framework.

### Performance Benchmarks

| Algorithm | Best Use Case | Key Advantage |
| --- | --- | --- |
| **TF-IDF** | General keyword matching | Efficient for smaller datasets and exact matches. |
| **BM25** | Dense document corpuses | Handles term saturation and document length normalization. |
| **Query Expansion** | Broad discovery | Increases recall by identifying semantic synonyms. |

---

## 📐 Mathematical Framework

### 1. Vector Space Model (TF-IDF)

The importance of a term $t$ in document $d$ is determined by:


$$TF-IDF(t, d) = TF(t, d) \cdot \log\left(\frac{N}{1 + df_t}\right)$$

### 2. Probabilistic Ranking (BM25)

To prevent long documents from unfairly dominating search results, we implement the BM25 formula:


$$score(D, Q) = \sum_{q \in Q} IDF(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{avgdl})}$$

---

## 🔄 Search Execution Pipeline

1. **Input Normalization:** Query is converted to lowercase and punctuation is removed.
2. **Lexical Correction:** The system identifies and corrects spelling errors using Levenshtein Distance.
3. **Semantic Expansion:** Synonyms are fetched via WordNet to broaden the search net.
4. **Scoring & Ranking:** The engine calculates scores based on the selected algorithm.
5. **Presentation:** Results are displayed with dynamically generated snippets and category labels.

---

## 👩‍💻 Research Team

**National University of Technology (NUTECH)** *Department of Computer Science*

| Name | Institutional Email |
| --- | --- |
| **Eman Asghar** | emankainif23@nutech.edu.pk |
| **Aena Habib** | aenahabibf23@nutech.edu.pk |
| **Dua Kamal** | duakamalf23@nutech.edu.pk |
| **Aleena Tahir** | aleenatahirf23@nutech.edu.pk |
| **Saqlain Abbas** | saqlainabbas@nutech.edu.pk |

---

## 🚀 Deployment Guide

### Local Environment

```bash
# Initialize environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch application
streamlit run app.py

```

### Docker Implementation

```bash
docker compose up --build

```

---

## 📄 License

This project is licensed under the **MIT License**.

Copyright (c) 2026 QueryLens 
