"""Semantic search over pre-computed DIT framework embeddings."""
import json
import numpy as np
from pathlib import Path

class SearchEngine:
    """Search engine with 3 tiers: semantic (OpenAI), TF-IDF fallback, empty fallback.

    Embeddings and manifest are loaded eagerly at init (fast: ~50ms).
    sklearn/TF-IDF is built lazily on first search that needs it (slow: ~2-3s)
    so that app startup and non-search pages are not penalized.
    """

    def __init__(self, embeddings_dir: Path = None):
        self.embeddings_dir = embeddings_dir or Path(__file__).parent.parent / "data" / "embeddings"
        self._embeddings = None
        self._manifest = None
        self._tfidf_matrix = None
        self._tfidf_vectorizer = None
        self._tfidf_ready = False
        self._load()

    def _load(self):
        """Load pre-computed embeddings and manifest from disk (no sklearn)."""
        emb_path = self.embeddings_dir / "embeddings.npy"
        man_path = self.embeddings_dir / "manifest.json"
        if emb_path.exists() and man_path.exists():
            self._embeddings = np.load(emb_path)
            with open(man_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._manifest = data["chunks"]
            print(f"SearchEngine loaded {len(self._manifest)} chunks ({self._embeddings.shape[1]}d)")
        else:
            print(f"SearchEngine: No embeddings found at {self.embeddings_dir}. Using TF-IDF only.")
            self._load_from_source()

    def _load_from_source(self):
        """Load chunks from source markdown files (no embeddings)."""
        source_dir = self.embeddings_dir.parent / "source"
        if not source_dir.exists():
            print("SearchEngine: No source files found. Search will return empty results.")
            return
        from embeddings.chunker import MarkdownChunker
        from dataclasses import asdict
        chunker = MarkdownChunker()
        chunks = chunker.chunk_all(source_dir)
        self._manifest = [asdict(c) for c in chunks]
        print(f"SearchEngine loaded {len(self._manifest)} chunks from source (TF-IDF only)")

    def _ensure_tfidf(self):
        """Build TF-IDF index on first use (lazy-loads sklearn)."""
        if self._tfidf_ready or not self._manifest:
            return
        from sklearn.feature_extraction.text import TfidfVectorizer
        texts = [c["text"] for c in self._manifest]
        self._tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(texts)
        self._tfidf_ready = True

    def search(self, query: str, top_k: int = 5) -> list:
        """Search for chunks most relevant to query."""
        if not self._manifest:
            return []

        # Try semantic search first (requires OPENAI_API_KEY)
        query_embedding = self._embed_query(query)

        if query_embedding is not None and self._embeddings is not None:
            # numpy cosine similarity — avoids sklearn import for the common path
            norms = np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(query_embedding)
            norms[norms == 0] = 1  # avoid division by zero
            similarities = self._embeddings @ query_embedding / norms
            top_indices = np.argsort(similarities)[::-1][:top_k]
            return [
                {**self._manifest[i], "score": float(similarities[i])}
                for i in top_indices
            ]

        # Fall back to TF-IDF (lazy-loads sklearn on first call)
        return self._tfidf_search(query, top_k)

    def _embed_query(self, query: str):
        """Embed query using OpenAI. Returns None if unavailable."""
        try:
            from openai import OpenAI
            import os
            if not os.environ.get("OPENAI_API_KEY"):
                return None
            client = OpenAI()
            response = client.embeddings.create(input=[query], model="text-embedding-3-large")
            return np.array(response.data[0].embedding)
        except Exception:
            return None

    def _tfidf_search(self, query: str, top_k: int) -> list:
        """Fallback keyword search using TF-IDF cosine similarity."""
        self._ensure_tfidf()
        if self._tfidf_vectorizer is None or self._tfidf_matrix is None:
            return []
        from sklearn.metrics.pairwise import cosine_similarity
        query_vec = self._tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self._tfidf_matrix)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [
            {**self._manifest[i], "score": float(similarities[i])}
            for i in top_indices
            if similarities[i] > 0
        ]
