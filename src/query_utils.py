"""Utility helpers for query normalization and query fusion variants."""

from __future__ import annotations

import re
from typing import List, Optional, Sequence


# Common stopwords to filter out when extracting topical keywords
_STOPWORDS = {
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
    "does",
    "do",
    "did",
    "is",
    "are",
    "was",
    "were",
    "can",
    "could",
    "should",
    "would",
    "may",
    "might",
    "will",
    "shall",
    "i",
    "me",
    "my",
    "we",
    "you",
    "they",
    "he",
    "she",
    "it",
    "this",
    "that",
    "these",
    "those",
    "them",
    "to",
    "for",
    "of",
    "and",
    "or",
    "the",
    "a",
    "an",
    "in",
    "on",
    "with",
    "into",
    "from",
    "about",
    "need",
    "show",
    "list",
    "find",
    "get",
    "tell",
    "give",
    "using",
    "use",
    "available",
    "availability",
    "piece",
    "pieces",
    "integration",
    "integrations",
    "action",
    "actions",
    "trigger",
    "triggers",
    "connector",
    "connectors",
    "flow",
    "flows",
    "activepieces",
}


def normalize_query(text: str) -> str:
    """Normalize query text by trimming and collapsing whitespace."""
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized


def _extract_topic_phrase(normalized_query: str, max_tokens: int = 6) -> str:
    """Extract a topical phrase by removing stopwords while preserving order."""
    tokens = re.findall(r"\b\w+\b", normalized_query)
    filtered: List[str] = []

    for token in tokens:
        if token.lower() in _STOPWORDS:
            continue
        filtered.append(token)
        if len(filtered) >= max_tokens:
            break

    return " ".join(filtered)


def generate_query_variants(user_query: str, min_variants: int = 3) -> List[str]:
    """Generate diversified query variants for query-fusion style retrieval."""
    normalized = normalize_query(user_query)
    if not normalized:
        return []

    variants: List[str] = []
    seen = set()

    def add_variant(candidate: str) -> None:
        cleaned = normalize_query(candidate)
        if not cleaned:
            return
        key = cleaned.lower()
        if key in seen:
            return
        seen.add(key)
        variants.append(cleaned)

    add_variant(normalized)

    topic_phrase = _extract_topic_phrase(normalized)
    if topic_phrase:
        add_variant(f"ActivePieces {topic_phrase} integrations")
        add_variant(f"{topic_phrase} ActivePieces pieces")
        add_variant(f"{topic_phrase} automation in ActivePieces")
    else:
        add_variant(f"{normalized} ActivePieces")
        add_variant(f"ActivePieces {normalized}")

    fallback_variants = [
        f"{normalized} integrations",
        f"{normalized} automation",
        f"{normalized} setup ActivePieces",
        f"{normalized} use cases",
        f"{normalized} documentation ActivePieces",
    ]

    for variant in fallback_variants:
        if len(variants) >= min_variants:
            break
        add_variant(variant)

    # Ensure we return at least min_variants by adding simple disambiguators if needed
    counter = 1
    while len(variants) < min_variants:
        add_variant(f"{normalized} ActivePieces reference {counter}")
        counter += 1

    return variants


_DOMAIN_PHRASES = (
    "activepieces",
    "active pieces",
    "flow builder",
    "build flow",
    "automation",
    "webhook",
    "web hook",
    "zapier",
    "make.com",
    "make com",
    "typebot",
    "faiss",
    "rag",
    "code step",
    "trigger step",
)

_DOMAIN_TOKENS = {
    "activepieces",
    "active",
    "pieces",
    "flow",
    "builder",
    "automation",
    "automations",
    "trigger",
    "triggers",
    "action",
    "actions",
    "integration",
    "integrations",
    "webhook",
    "webhooks",
    "step",
    "steps",
    "run",
    "code",
    "typescript",
    "slack",
    "gmail",
    "notion",
    "database",
    "vector",
    "search",
    "plan",
    "builder",
    "workflow",
    "workflows",
    "api",
    "key",
    "keys",
    "piece",
    "pieces",
    "schedule",
    "cron",
}

def _matches_domain(normalized_text: str) -> bool:
    """Return True when the normalized text clearly references the domain."""
    if not normalized_text:
        return False

    lowered = normalized_text.lower()

    for phrase in _DOMAIN_PHRASES:
        if phrase in lowered:
            return True

    tokens = re.findall(r"\b\w+\b", lowered)
    token_hits = sum(1 for token in tokens if token in _DOMAIN_TOKENS)

    return token_hits >= 2


def is_activepieces_query(user_query: str, history: Optional[Sequence[str]] = None) -> bool:
    """Heuristically determine if the query is about ActivePieces or workflow automation.

    When available, recent conversation history is considered so that short follow-up
    prompts (e.g. "add another step") still route to the agent if the dialogue has
    been about ActivePieces.
    """

    normalized = normalize_query(user_query)
    if _matches_domain(normalized):
        return True

    if not history:
        return False

    recent_snippets: List[str] = []
    for entry in reversed(history):
        if len(recent_snippets) >= 6:
            break
        normalized_entry = normalize_query(entry)
        if not normalized_entry:
            continue
        recent_snippets.append(normalized_entry)
        if _matches_domain(normalized_entry):
            return True

    if not recent_snippets:
        return False

    # Combine recent snippets to capture distributed clues across turns
    combined = " ".join([normalized] + recent_snippets).strip()
    if not combined:
        return False

    return _matches_domain(combined)

