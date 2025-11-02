import os
import sqlite3
import json
import re
from typing import List, Dict, Tuple

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

_conn: sqlite3.Connection | None = None
_tokenizer = None
_model = None


def init_vector_store(db_name: str = "vectors.db", model_name: str = "asafaya/bert-base-arabic"):
    global _conn, _tokenizer, _model

    # Initialize SQLite
    _conn = sqlite3.connect(db_name, check_same_thread=False)
    cur = _conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            date TEXT,
            embedding TEXT NOT NULL
        )
        """
    )
    _conn.commit()

    # Load AraBERT tokenizer and model (no sentence-transformers dependency)
    _tokenizer = AutoTokenizer.from_pretrained(model_name)
    _model = AutoModel.from_pretrained(model_name)
    _model.eval()


# ---------------- Arabic Normalization & Tokenization ---------------- #
_ALEF_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ئ": "ي", "ؤ": "و", "ة": "ه"})
_EASTERN_NUMS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_DIACRITICS_RE = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0657-\u065F\u0670\u06D6-\u06ED]")
_NON_LETTER_RE = re.compile(r"[^\u0621-\u063A\u0641-\u064A0-9\s]")

# Name aliases and synonyms for smart matching
_NAME_ALIASES = {
    # Football players
    "فيتي": "فينيسيوس",
    "فيني": "فينيسيوس",
    "كريس": "كريستيانو رونالدو",
    "رونالدو": "كريستيانو رونالدو",
    "ميسي": "ليونيل ميسي",
    "كيليان": "مبابي",
    "نيمار": "نيمار دا سيلفا",
    "بنزيما": "كريم بنزيما",
    "صلاح": "محمد صلاح",
    "مودريتش": "لوكا مودريتش",
    # Teams
    "الريال": "ريال مدريد",
    "البارسا": "برشلونة",
    "الاتحاد": "اتحاد جدة",
    "الهلال": "الهلال السعودي",
    "النصر": "النصر السعودي",
    # Common terms
    "جزاء": "ركلة جزاء",
    "احتجاج": "اعتراض",
    "فيتو": "اعتراض",
    "بطاقة": "كرت",
    "حمراء": "احمر",
    "صفراء": "اصفر",
}


def _normalize_ar(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    t = _DIACRITICS_RE.sub("", t)
    t = t.replace("ـ", "")
    t = t.translate(_ALEF_MAP)
    t = t.translate(_EASTERN_NUMS)
    t = _NON_LETTER_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t)
    return t


def _expand_aliases(text: str) -> str:
    """Expand common name aliases and synonyms in the text."""
    normalized = _normalize_ar(text)
    words = normalized.split()
    expanded = []
    
    for word in words:
        # Check if this word has an alias
        found = False
        for alias, full_name in _NAME_ALIASES.items():
            if _normalize_ar(alias) == word:
                # Add both the original word and the full name
                expanded.append(word)
                expanded.extend(_normalize_ar(full_name).split())
                found = True
                break
        if not found:
            expanded.append(word)
    
    return " ".join(expanded)


def _token_set(text: str) -> set:
    # First expand aliases, then normalize
    expanded = _expand_aliases(text)
    toks = [w for w in expanded.split() if len(w) >= 2]
    return set(toks)


def _mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    masked = last_hidden_state * mask
    summed = masked.sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


def _embed_text(text: str) -> List[float]:
    # Expand aliases first, then normalize - this helps the model understand abbreviations
    expanded = _expand_aliases(text)
    inputs = _tokenizer(
        expanded,
        max_length=256,
        truncation=True,
        padding=True,
        return_tensors="pt",
    )
    with torch.no_grad():
        outputs = _model(**inputs)
        pooled = _mean_pool(outputs.last_hidden_state, inputs["attention_mask"])  # [1, hidden]
        vec = pooled[0].cpu().numpy().astype(np.float32)
        # L2 normalize for cosine similarity via dot product
        norm = np.linalg.norm(vec) + 1e-12
        vec = (vec / norm).tolist()
        return vec


def upsert_articles(articles: List[Dict]):
    """Insert or update a batch of articles with embeddings.
    Each article: {title, body, url, date}
    """
    global _conn
    if _conn is None:
        raise RuntimeError("Vector store not initialized. Call init_vector_store() first.")

    cur = _conn.cursor()
    added = 0
    for a in articles:
        try:
            text = f"Title: {a['title']}\nBody: {a['body']}"
            emb = _embed_text(text)
            cur.execute(
                """
                INSERT INTO articles (url, title, body, date, embedding)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    body=excluded.body,
                    date=excluded.date,
                    embedding=excluded.embedding
                """,
                (a["url"], a["title"], a["body"], a.get("date"), json.dumps(emb)),
            )
            added += 1
        except Exception as e:
            print(f"Embedding/upsert failed for {a.get('url')}: {e}")

    _conn.commit()
    print(f"VectorStore: upserted {added} articles.")


DEFAULT_SIM_THRESHOLD = float(os.getenv("SIM_THRESHOLD", "0.45"))


def search(query: str, top_k: int = 8, threshold: float = DEFAULT_SIM_THRESHOLD) -> Tuple[List[Dict], bool, float]:
    """Return top_k most similar articles to the query embedding.
    Returns (contexts, is_relevant, best_similarity_score)
    """
    global _conn
    if _conn is None:
        raise RuntimeError("Vector store not initialized. Call init_vector_store() first.")

    qvec = np.array(_embed_text(query), dtype=np.float32)
    q_tokens = _token_set(query)

    cur = _conn.cursor()
    cur.execute("SELECT url, title, body, date, embedding FROM articles")
    rows = cur.fetchall()
    if not rows:
        return [], False, 0.0

    sims: List[Tuple[float, Dict]] = []
    for url, title, body, date, emb_json in rows:
        try:
            dvec = np.array(json.loads(emb_json), dtype=np.float32)
            # Cosine similarity since vectors are normalized
            sim = float(np.dot(qvec, dvec))
            # Add simple lexical Jaccard overlap between query and doc
            doc_tokens = _token_set(f"{title} {body[:400]}")
            union = q_tokens | doc_tokens
            jacc = (len(q_tokens & doc_tokens) / float(len(union))) if union else 0.0
            combined = 0.8 * sim + 0.2 * jacc
            sims.append(
                (
                    combined,
                    {
                        "url": url,
                        "title": title,
                        "body": body[:600],
                        "date": date,
                        "similarity": combined,
                        "sim_raw": sim,
                        "lexical": jacc,
                    },
                )
            )
        except Exception as e:
            continue

    sims.sort(key=lambda x: x[0], reverse=True)
    top_results = sims[:top_k]
    top_contexts = [item[1] for item in top_results]

    # --- Detailed Logging for Debugging ---
    is_relevant = False
    best_sim = 0.0
    if top_results:
        top_scores = [s[0] for s in top_results[:3]]
        best_sim = top_scores[0] if top_scores else 0.0
        print(f"DEBUG: Top 3 combined scores: {[f'{score:.4f}' for score in top_scores]}")
        print(f"DEBUG: Threshold is {threshold:.4f}")
        
        # Consider relevant if ANY of the top 3 results are above the threshold
        if any(score >= threshold for score in top_scores):
            is_relevant = True
            print("DEBUG: Relevance check PASSED. (is_relevant = True)")
        else:
            print("DEBUG: Relevance check FAILED. All top scores are below threshold. (is_relevant = False)")
    else:
        print("DEBUG: No results found in vector store search.")

    return top_contexts, is_relevant, best_sim
