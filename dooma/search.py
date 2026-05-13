"""Fuzzy search across the question index using rapidfuzz."""

from __future__ import annotations

from rapidfuzz import fuzz, process

from dooma.models import Index, Question


def fuzzy_search(query: str, index: Index, *, limit: int = 20) -> list[Question]:
    """Search questions by title, patterns, and topics.

    Parameters
    ----------
    query : str
        Free-text search query.
    index : Index
        The in-memory question index.
    limit : int
        Maximum number of results to return.

    Returns
    -------
    list[Question]
        Matching questions sorted by relevance (best first).
    """
    if not query or not query.strip():
        return []
    if limit < 1:
        return []

    query = query.strip().lower()

    # Build a search corpus: each entry is (search_text, question_id)
    corpus: list[tuple[str, str]] = []
    for qid, q in index.questions.items():
        # Primary: title
        corpus.append((q.title.lower(), qid))
        # Secondary: patterns and topics
        for pat in q.patterns:
            corpus.append((pat.replace("-", " "), qid))
        for topic in q.topics:
            corpus.append((topic.replace("-", " "), qid))

    if not corpus:
        return []

    # Use rapidfuzz process.extract for fast matching
    texts = [c[0] for c in corpus]
    results = process.extract(
        query,
        texts,
        scorer=fuzz.WRatio,
        limit=min(limit * 3, len(texts)),  # over-fetch to deduplicate
        score_cutoff=50,
    )

    # Deduplicate by question_id, keeping highest score
    seen: dict[str, float] = {}
    for text, score, idx in results:
        qid = corpus[idx][1]
        if qid not in seen or score > seen[qid]:
            seen[qid] = score

    # Sort by score desc, take top `limit`
    ranked = sorted(seen.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [index.questions[qid] for qid, _ in ranked if qid in index.questions]
