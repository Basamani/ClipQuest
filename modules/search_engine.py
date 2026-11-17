from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


_model = None


def get_embedding_model():
    """Load the semantic search model only when needed."""
    global _model

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def build_search_index(segments):
    """Create embeddings for valid timestamped transcript segments."""
    valid_segments = [
        {
            **segment,
            "text": str(segment.get("text", "")).strip()
        }
        for segment in segments or []
        if isinstance(segment, dict)
        and str(segment.get("text", "")).strip()
    ]

    if not valid_segments:
        return {
            "segments": [],
            "embeddings": None
        }

    model = get_embedding_model()
    texts = [segment["text"] for segment in valid_segments]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return {
        "segments": valid_segments,
        "embeddings": embeddings
    }


def search_segments(query, search_index, top_k=5):
    """Find transcript segments most similar to a question."""
    if not isinstance(query, str) or not query.strip():
        return []

    if not isinstance(search_index, dict):
        return []

    segments = search_index.get("segments", [])
    embeddings = search_index.get("embeddings")

    if not segments or embeddings is None:
        return []

    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = 5

    if top_k <= 0:
        return []

    model = get_embedding_model()
    query_embedding = model.encode(
        [query.strip()],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    scores = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    ranked_indices = scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:
        result = dict(segments[index])
        result["score"] = round(float(scores[index]), 4)
        results.append(result)

    return results