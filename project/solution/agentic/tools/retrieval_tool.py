
import json
import re
from pathlib import Path
from typing import Dict, Any, List


def _load_articles() -> List[Dict[str, Any]]:
    """Load KB articles from JSONL under solution/data/external."""
    root = Path(__file__).resolve().parents[2]  # .../solution
    path = root / "data" / "external" / "cultpass_articles.jsonl"
    articles = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                articles.append(json.loads(line))
    return articles


def _tokenize(text: str) -> List[str]:
    text = text.lower()
    return re.findall(r"[a-z0-9]+", text)


def retrieve_articles(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Retrieve relevant knowledge base articles using a simple keyword overlap score.

    Returns:
      {
        "results": [
            {"title": ..., "tags": ..., "snippet": ..., "score": 0.0..1.0}
        ],
        "query": query
      }
    """
    articles = _load_articles()
    q_tokens = set(_tokenize(query))

    scored = []
    for a in articles:
        title = a.get("title", "")
        content = a.get("content", "")
        tags = a.get("tags", "")

        doc_text = f"{title}\n{content}\n{tags}"
        d_tokens = set(_tokenize(doc_text))

        # overlap score (very lightweight, explainable)
        overlap = len(q_tokens.intersection(d_tokens))
        denom = max(1, len(q_tokens))
        base_score = overlap / denom

        # small boost if query mentions tag words
        tag_tokens = set(_tokenize(tags))
        tag_overlap = len(q_tokens.intersection(tag_tokens))
        score = min(1.0, base_score + (0.1 if tag_overlap > 0 else 0.0))

        snippet = content[:300].replace("\n", " ").strip()

        scored.append({
            "title": title,
            "tags": tags,
            "snippet": snippet,
            "score": float(round(score, 3)),
            "full_content": content  # analysis agent can use it
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    results = [r for r in scored[:top_k] if r["score"] > 0]

    return {
        "query": query,
        "results": results,
        "count": len(results)
    }
