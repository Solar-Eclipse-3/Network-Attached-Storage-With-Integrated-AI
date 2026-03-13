from __future__ import annotations
import os
from typing import List, Optional

DEFAULT_EMBED_MODEL = os.getenv("RAG_EMBED_MODEL") or "text-embedding-3-small"

def embed_texts(texts: List[str], *, api_key: Optional[str]=None, model: str=DEFAULT_EMBED_MODEL) -> List[List[float]]:
    if not texts:
        return []
    api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("No OPENAI_API_KEY/API_KEY set for embeddings")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]
