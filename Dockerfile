# ── Dockerfile ──────────────────────────────────────────────────────────────
# Build:  docker build -t noor-search .
# Run:    docker run -p 8501:8501 noor-search

FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK resources so the container is self-contained
RUN python -c "\
import nltk; \
nltk.download('punkt', quiet=True); \
nltk.download('punkt_tab', quiet=True); \
nltk.download('stopwords', quiet=True); \
nltk.download('wordnet', quiet=True); \
nltk.download('omw-1.4', quiet=True);"

# Copy project files
COPY . .

# Create data directory (user mounts their CSV here)
RUN mkdir -p data

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
