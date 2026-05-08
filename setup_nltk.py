"""
setup_nltk.py — Run this ONCE before starting the app
======================================================
Usage:
    python setup_nltk.py

Downloads all NLTK data the search engine needs.
This only needs to be done one time per machine.
"""

import nltk
import sys

packages = [
    "punkt",
    "punkt_tab",
    "stopwords",
    "wordnet",
    "omw-1.4",
]

print("=" * 50)
print("  Noor Search Engine — NLTK Setup")
print("=" * 50)

all_ok = True
for pkg in packages:
    print(f"  Downloading: {pkg} ...", end=" ", flush=True)
    result = nltk.download(pkg, quiet=True)
    if result:
        print("✓")
    else:
        print("✗ FAILED")
        all_ok = False

print("=" * 50)
if all_ok:
    print("  ✅ All packages downloaded successfully!")
    print("  You can now run:  streamlit run app.py")
else:
    print("  ⚠️  Some downloads failed. Check your internet connection.")
    print("  Try running this script again.")
    sys.exit(1)

print("=" * 50)
