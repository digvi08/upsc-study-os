"""General utility helpers."""
import re
import math
from typing import Any, Dict, List, Optional
from datetime import datetime, date


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return re.sub(r"^-+|-+$", "", text)


def paginate(query, page: int, page_size: int) -> Dict[str, Any]:
    """Apply pagination to a SQLAlchemy query and return metadata."""
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def truncate(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max_length characters."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """Simple keyword extraction by frequency (no NLP dependency)."""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "this", "that", "these",
        "those", "it", "its", "as", "if", "then", "than", "so", "yet",
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    freq: Dict[str, int] = {}
    for word in words:
        if word not in stop_words:
            freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]


def format_duration(minutes: int) -> str:
    """Format minutes into human-readable duration."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m" if mins else f"{hours}h"


def date_range(start: date, end: date) -> List[date]:
    """Generate list of dates between start and end (inclusive)."""
    from datetime import timedelta
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division returning default if denominator is zero."""
    return numerator / denominator if denominator != 0 else default
